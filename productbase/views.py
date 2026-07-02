from rest_framework import viewsets, mixins, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import CharFilter, FilterSet
from django.db import transaction
from django.db.models import Count, F, Q, Sum, Subquery
from django.utils import timezone
from django.http import HttpResponse
import openpyxl
from .models import (BaseProductGroup, ProductGroup, ProductCore, ProductShop,
                     ProductImage, FetchTask, Supplier, ProductSeries,
                     ProductLog, log_product_action,
                     ShopConfig, ListingConfig, FetchConfig, PricingRule,
                     DifyUsageLog, VariantMappingAttribute, WarehouseConfig)
from .serializers import (BaseProductGroupSerializer, BaseProductGroupListSerializer,
                           ProductGroupSerializer, FetchTaskSerializer,
                           SupplierSerializer, ProductSeriesSerializer,
                           ProductLogSerializer, ShopConfigSerializer,
                           ListingConfigSerializer, FetchConfigSerializer,
                           PricingRuleSerializer, VariantMappingAttributeSerializer,
                           WarehouseConfigSerializer)
from .permissions import IsOwnerOrAdmin
from setting.models import OperateLog
from productbase import tasks


class DefaultPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 1000


class FetchTaskViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = FetchTaskSerializer
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filter_fields = ('platform', 'creator', 'status')
    search_fields = ('item_id', )

    def get_queryset(self):
        return FetchTask.objects.all().select_related("base_group").order_by(
            "-create_time")


class BaseProductGroupFilter(FilterSet):
    """自定义过滤器：SKU/标题搜索用子查询替代 JOIN LIKE，避免全表扫描超时"""
    sku = CharFilter(method='filter_sku', label='SKU 搜索')
    title = CharFilter(method='filter_title', label='标题搜索')

    def filter_sku(self, queryset, name, value):
        # SKU 格式如 Z04667，用 startswith 可利用索引
        matching_ids = ProductCore.objects.filter(
            sku__startswith=value
        ).values_list('base_id', flat=True)[:1000]
        return queryset.filter(id__in=list(matching_ids))

    def filter_title(self, queryset, name, value):
        matching_ids = ProductGroup.objects.filter(
            title__icontains=value
        ).values_list('base_id', flat=True)[:1000]
        return queryset.filter(id__in=list(matching_ids))

    class Meta:
        model = BaseProductGroup
        fields = ['p_status', 'category', 'from_platform', 'creator',
                  'image_migrated', 'variant_mapped', 'sku', 'title']


class BaseProductGroupViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet):
    serializer_class = BaseProductGroupSerializer
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filterset_class = BaseProductGroupFilter
    search_fields = ('category', 'from_item_id', 'tag', 'supplier', 'series')
    ordering_fields = ('create_time', )

    queryset = BaseProductGroup.objects.all().order_by("-create_time")

    def get_serializer_class(self):
        if self.action == 'list':
            return BaseProductGroupListSerializer
        return BaseProductGroupSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        try:
            ctx['variant_page'] = int(
                self.request.query_params.get('variant_page', 1))
        except (ValueError, TypeError):
            ctx['variant_page'] = 1
        try:
            ctx['variant_page_size'] = int(
                self.request.query_params.get('variant_page_size', 20))
        except (ValueError, TypeError):
            ctx['variant_page_size'] = 20
        return ctx

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            qs = qs.annotate(
                sku_count=Count('core_skus', distinct=True),
                group_count=Count('product_groups', distinct=True),
                _synced_sku_count=Count('core_skus', filter=Q(core_skus__sku_synced_at__isnull=False)),
                _synced_shop_count=Count('product_groups', filter=Q(product_groups__shop_synced_at__isnull=False), distinct=True),
            ).prefetch_related('product_groups__images')
        if self.action == 'retrieve':
            from django.db.models import Prefetch
            # shop_skus: select_related core_sku(FK) + prefetch core_sku images
            shop_skus_qs = ProductShop.objects.select_related(
                'core_sku'
            ).prefetch_related('core_sku__images')
            # product_groups: select_related listing_config(FK) + prefetch shop_skus/images
            pgs_qs = ProductGroup.objects.select_related(
                'listing_config'
            ).prefetch_related(
                Prefetch('shop_skus', queryset=shop_skus_qs),
                'images',
            )
            qs = qs.prefetch_related(
                Prefetch('product_groups', queryset=pgs_qs),
                'logs',
            )
        return qs

    @action(methods=['post'],
            detail=False,
            url_path='upload_image',
            url_name='upload_image')
    def upload_image(self, request):
        """
        上传图片文件到聚合图床，返回 CDN URL。
        Content-Type: multipart/form-data, 字段名: file
        """
        file = request.FILES.get('file')
        if not file:
            return Response({'error': '请上传图片文件，字段名: file'},
                            status=status.HTTP_400_BAD_REQUEST)

        from productbase.image_hosting import upload_image_file
        url = upload_image_file(file.read(), filename=file.name)
        if url:
            return Response({'url': url})
        return Response({'error': '上传失败，请重试'},
                        status=status.HTTP_502_BAD_GATEWAY)

    @action(methods=['post'],
            detail=True,
            url_path='product_groups',
            url_name='add_product_group')
    def add_product_group(self, request, pk=None):
        """
        新增店铺。自动为所有已有 ProductCore 创建 ProductShop，
        可选传入 variants 设置每个 SKU 的变体值和价格。
        """
        from productbase.serializers import (ProductGroupCreateSerializer,
                                              ProductGroupSerializer)

        base = self.get_object()
        serializer = ProductGroupCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pg = serializer.save(base=base)

        log_product_action(base, 'ADD_SHOP',
                           f'新增店铺: {pg.shop_account} ({pg.platform})',
                           operator=request.user.username)

        return Response(ProductGroupSerializer(pg).data,
                        status=status.HTTP_201_CREATED)

    @action(methods=['post'],
            detail=True,
            url_path='mark_ready',
            url_name='mark_ready')
    def mark_ready(self, request, pk=None):
        """
        将产品从 PREPARING 转为 READY。
        前置条件：image_migrated=True 且 variant_mapped=True。
        """
        base = self.get_object()

        if base.p_status != 'PREPARING':
            return Response(
                {'error': f'当前状态为 {base.p_status}，只有 PREPARING 状态可以转为 READY'},
                status=status.HTTP_400_BAD_REQUEST)

        errors = []
        if not base.image_migrated:
            errors.append('图片迁移未完成')
        if not base.variant_mapped:
            errors.append('变体映射未完成')

        if errors:
            return Response({'error': '；'.join(errors)},
                            status=status.HTTP_400_BAD_REQUEST)

        base.p_status = 'READY'
        base.save(update_fields=['p_status'])

        from productbase.models import log_product_action
        log_product_action(base, 'STATUS_CHANGE',
                           'PREPARING → READY',
                           operator=request.user.username)

        serializer = self.get_serializer(base)
        return Response(serializer.data)

    @action(methods=['post'],
            detail=False,
            url_path='export_skus',
            url_name='export_skus')
    def export_skus(self, request):
        """导出 SKU 为 Excel。仅导出 READY 状态的产品"""
        ids = request.data.get('ids')
        creator = request.data.get('creator')

        base_filter = {'base__p_status': 'READY'}

        if ids:
            cores = ProductCore.objects.filter(
                base_id__in=ids, **base_filter).select_related('base')
        elif creator:
            cores = ProductCore.objects.filter(
                base__creator=creator, **base_filter).filter(
                    Q(sku_synced_at__isnull=True)
                    | Q(updated_at__gt=F('sku_synced_at'))).select_related(
                        'base')
        else:
            user_filter = request.user.username if request.user.is_authenticated else 'system'
            cores = ProductCore.objects.filter(
                base__creator=user_filter, **base_filter).filter(
                    Q(sku_synced_at__isnull=True)
                    | Q(updated_at__gt=F('sku_synced_at'))).select_related(
                        'base')

        if not cores.exists():
            return Response({'msg': '没有需要导出的 SKU', 'status': 'empty'},
                            status=status.HTTP_200_OK)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'SKU导出'
        headers = [
            '*库存sku编号', '*库存sku中文名称', '商品重量', '统一成本价(RMB)', '仓库',
            '供应商', '供应商商品网址', '库存图片地址'
        ]
        ws.append(headers)
        # 预加载封面图片，避免 N+1
        core_ids_list = [c.id for c in cores]
        cover_map = {}
        if core_ids_list:
            covers = ProductImage.objects.filter(
                product_core_id__in=core_ids_list, is_cover=True
            ).values('product_core_id', 'image_url')
            for item in covers:
                cover_map[item['product_core_id']] = item['image_url']
        for core in cores:
            ws.append([
                core.sku, core.p_name, 70,
                float(core.cost), core.warehouse or 'F仓', core.base.supplier or '',
                core.purchase_url or '',
                cover_map.get(core.id, '')
            ])
        for col in ['A', 'B', 'G']:
            ws.column_dimensions[col].width = 30

        resp = HttpResponse(
            content_type=
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename=sku_export.xlsx'
        wb.save(resp)
        # 导出成功后标记已同步（在 save 之后，避免生成失败误标记）
        core_ids = list(cores.values_list('id', flat=True))
        ProductCore.objects.filter(id__in=core_ids).update(
            sku_synced_at=timezone.now())
        # 记录导出日志
        base_skus = {}
        for c in cores:
            base_skus.setdefault(c.base_id, []).append(c.id)
        for bid, sku_list in base_skus.items():
            log_product_action(BaseProductGroup.objects.get(id=bid),
                               'EXPORT_SKU',
                               f'导出 {len(sku_list)} 个 SKU',
                               operator=request.user.username)
        return resp

    def perform_update(self, serializer):
        """更新 BaseProductGroup 后，自动重新生成所有 SKU 的 p_name"""
        instance = serializer.save()
        from productbase.tasks import (regenerate_p_names,
                                       update_variant_mapped_status)
        regenerate_p_names(instance)
        update_variant_mapped_status(instance.id)

    def perform_destroy(self, instance):
        log_product_action(instance, 'DELETE',
                           f'删除产品: {instance.category or instance.id}',
                           operator=self.request.user.username)
        instance.delete()

    @action(methods=['post'], detail=False, url_path='batch_delete')
    def batch_delete(self, request):
        ids = request.data.get("ids", [])

        if not isinstance(ids, list) or len(ids) == 0:
            return Response({
                'msg': 'ids 必须是非空数组',
                'status': 'error'
            },
                            status=status.HTTP_202_ACCEPTED)

        try:
            with transaction.atomic():
                # 删前记录日志
                bases = list(BaseProductGroup.objects.filter(id__in=ids))
                for base in bases:
                    log_product_action(base, 'DELETE',
                                       f'批量删除产品',
                                       operator=request.user.username)
                delete_count = len(bases)
                BaseProductGroup.objects.filter(id__in=ids).delete()

            return Response(
                {
                    'msg': f'删除成功{delete_count}条，失败0条',
                    'status': 'success'
                },
                status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'msg': f'删除成功0条，失败{len(ids)}条',
                'status': 'error'
            },
                            status=status.HTTP_202_ACCEPTED)

    @action(methods=['post'], detail=True, url_path='delete_core_sku')
    def delete_core_sku(self, request, pk=None):
        """按 Core SKU ID 删除变体（级联删除所有店铺的对应记录）"""
        base = self.get_object()
        core_sku_id = request.data.get('core_sku_id')
        if not core_sku_id:
            return Response(
                {'msg': 'core_sku_id 不能为空', 'status': 'error'},
                status=status.HTTP_400_BAD_REQUEST)

        core = base.core_skus.filter(id=core_sku_id).first()
        if not core:
            return Response(
                {'msg': f'Core SKU id={core_sku_id} 不存在', 'status': 'error'},
                status=status.HTTP_404_NOT_FOUND)

        sku_code = core.sku
        with transaction.atomic():
            core.delete()  # CASCADE 删除所有 ProductShop
            log_product_action(base, 'DELETE_SKU',
                               f'删除SKU: {sku_code}',
                               operator=request.user.username)

        return Response(
            {'msg': f'已删除 SKU: {sku_code}', 'status': 'success'},
            status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='update_product_supply')
    def update_product_supply(self, request):
        ids = request.data.get("ids", [])
        supplier = request.data.get("supplier")
        series = request.data.get("series")
        cost = request.data.get("cost")

        if not isinstance(ids, list) or len(ids) == 0:
            return Response({
                'msg': 'ids 必须是非空数组',
                'status': 'error'
            },
                            status=status.HTTP_202_ACCEPTED)

        success_count = 0
        fail_count = 0

        try:
            with transaction.atomic():
                cost_val = None
                if cost is not None:
                    try:
                        cost_val = float(cost)
                    except ValueError:
                        cost_val = None

                update_fields = {}
                if supplier is not None:
                    update_fields["supplier"] = supplier.strip()
                if series is not None:
                    update_fields["series"] = series.strip()

                base_query = BaseProductGroup.objects.filter(id__in=ids)
                if update_fields:
                    success_count = base_query.update(**update_fields)

                # ======================== 【修改 2】更新成本到 ProductCore ========================
                if cost_val and cost_val > 0:
                    ProductCore.objects.filter(base__id__in=ids).update(
                        cost=cost_val, updated_at=timezone.now())

                fail_count = len(ids) - success_count

                # 更新供应商/系列后，重新生成 SKU 中文名称
                if supplier is not None or series is not None:
                    from productbase.tasks import regenerate_p_names
                    for base in BaseProductGroup.objects.filter(id__in=ids):
                        regenerate_p_names(base)

            tasks.check_and_update_base_status(ids)
            return Response(
                {
                    'msg': f'更新成功{success_count}条，失败{fail_count}条',
                    'status': 'success'
                },
                status=status.HTTP_200_OK)

        except Exception:
            fail_count = len(ids)
            return Response(
                {
                    'msg': f'更新成功{success_count}条，失败{fail_count}条',
                    'status': 'error'
                },
                status=status.HTTP_202_ACCEPTED)

    @action(methods=['post'], detail=False, url_path='fetch_product')
    def fetch_product(self, request):
        item_ids = request.data.get("item_ids", [])
        marketplace_id = request.data.get("marketplace_id")
        platform = request.data.get("platform", "EBAY")
        supplier = request.data.get("supplier")
        series = request.data.get("series")
        cost = request.data.get("cost", 0)

        if not item_ids or not isinstance(item_ids,
                                          list) or len(item_ids) == 0:
            return Response({"error": "item_ids 必须是数组且不能为空"}, status=400)
        if not marketplace_id:
            return Response({"error": "marketplace_id 不能为空"}, status=400)

        # 检查用户是否配置了主店铺
        if request.user.is_authenticated:
            has_main = ShopConfig.objects.filter(
                user=request.user, is_main=True).exists()
            if not has_main:
                return Response(
                    {'error': '请先配置主店铺（ShopConfig.is_main=True）'},
                    status=status.HTTP_400_BAD_REQUEST)

        creator_username = request.user.username if request.user.is_authenticated else "system"

        # 查用户启用的 FetchConfig
        fetch_config = None
        if request.user.is_authenticated:
            fetch_config = FetchConfig.objects.filter(
                user=request.user, is_active=True).first()

        keep_attributes = fetch_config.keep_attributes if fetch_config else None
        fixed_attributes = fetch_config.fixed_attributes if fetch_config else None
        fetch_config_name = fetch_config.name if fetch_config else None

        # 创建 FetchTask(PENDING) 并分发 Celery 异步任务
        result = []
        for item_id in item_ids:
            # 检查同一 item_id 是否已有未完成的任务
            existing = FetchTask.objects.filter(
                item_id=item_id,
                status__in=['PENDING', 'PROCESSING']
            ).first()
            if existing:
                result.append({
                    'task_id': existing.id,
                    'item_id': item_id,
                    'status': existing.status,
                    'msg': '已存在进行中的任务，跳过重复提交'
                })
                continue

            task = FetchTask.objects.create(
                item_id=item_id,
                marketplace_id=marketplace_id,
                platform=platform,
                status="PENDING",
                creator=creator_username,
                log="等待抓取")

            tasks.fetch_ebay_product_async.delay(
                task_id=task.id,
                supplier=supplier,
                series=series,
                cost=cost,
                creator=creator_username,
                keep_attributes=keep_attributes,
                fixed_attributes=fixed_attributes,
                fetch_config_name=fetch_config_name)

            result.append({
                "item_id": task.item_id,
                "status": "PENDING",
                "task_id": task.id
            })

        return Response(
            {
                "message": f"已接收 {len(result)} 个抓取任务，后台处理中",
                "results": result
            },
            status=status.HTTP_202_ACCEPTED)

    @action(methods=['post'], detail=False, url_path='check_exist')
    def check_exist(self, request):
        """检查产品是否已被抓取。传入 platform + item_ids，返回每个 item_id 是否存在"""
        platform = request.data.get("platform")
        item_ids = request.data.get("item_ids", [])

        if not platform:
            return Response({"error": "platform 不能为空"}, status=400)
        if not item_ids or not isinstance(item_ids, list):
            return Response({"error": "item_ids 必须是非空数组"}, status=400)

        # 批量查询存在的 item_id
        existing = set(
            BaseProductGroup.objects.filter(
                from_platform=platform,
                from_item_id__in=item_ids
            ).values_list("from_item_id", flat=True)
        )

        result = {item_id: item_id in existing for item_id in item_ids}
        return Response(result)

    @action(methods=['get'], detail=False, url_path='image_stats')
    def image_stats(self, request):
        """查询 CDN 与 DB 图片统计：CDN 总数、DB 总数、已迁移、未迁移、孤儿数"""
        from productbase.image_hosting import get_all_cdn_images, is_ebay_image

        cdn_map = get_all_cdn_images()  # {url: created_at}
        cdn_urls = set(cdn_map.keys())
        db_urls = set(
            ProductImage.objects.values_list('image_url', flat=True))

        unmigrated = sum(1 for u in db_urls if is_ebay_image(u))
        migrated = len(db_urls) - unmigrated

        return Response({
            'cdn_total': len(cdn_urls),
            'db_total': len(db_urls),
            'migrated': migrated,
            'unmigrated': unmigrated,
            'orphan': len(cdn_urls - db_urls),
        })

    @action(methods=['post'], detail=False, url_path='cleanup_images')
    def cleanup_images(self, request):
        """全量对比 CDN 与 DB，清理孤儿图片（排除最近5分钟内的，防止误删迁移中的图片）"""
        from datetime import datetime, timedelta
        from productbase.image_hosting import get_all_cdn_images, delete_cdn_images

        cdn_map = get_all_cdn_images()  # {url: created_at}
        db_urls = set(
            ProductImage.objects.values_list('image_url', flat=True))

        # 排除最近 5 分钟内创建的图片（可能在迁移中）
        cutoff = datetime.now() - timedelta(minutes=5)
        safe_urls = set()
        for url, created_at in cdn_map.items():
            if not created_at:
                safe_urls.add(url)
                continue
            try:
                t = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                if t < cutoff:
                    safe_urls.add(url)
            except ValueError:
                safe_urls.add(url)

        orphans = list(safe_urls - db_urls)

        if not orphans:
            return Response({'msg': '没有需要清理的图片', 'orphan': 0})

        deleted = 0
        failed = 0
        batch_size = 1000
        batches = (len(orphans) + batch_size - 1) // batch_size

        for i in range(0, len(orphans), batch_size):
            batch = orphans[i:i + batch_size]
            success, msg = delete_cdn_images(batch)
            if success:
                deleted += len(batch)
            else:
                failed += len(batch)
                print(f'[cleanup_images] batch failed: {msg}')

        return Response({
            'orphan': len(orphans),
            'deleted': deleted,
            'failed': failed,
            'batches': batches,
        })

    @action(methods=['post'], detail=True, url_path='retry_migration')
    def retry_migration(self, request, pk=None):
        """手动重新触发图片迁移（仅处理剩余未迁移的 eBay 图片）"""
        base = self.get_object()
        from productbase.tasks import check_has_ebay_images, migrate_images_to_cdn
        if not check_has_ebay_images(base.id):
            return Response(
                {'msg': '没有需要迁移的 eBay 图片', 'status': 'empty'},
                status=status.HTTP_200_OK)
        migrate_images_to_cdn.delay(base.id)
        log_product_action(base, 'IMAGE_MIGRATE',
                           '手动重新触发图片迁移',
                           operator=request.user.username)
        return Response({'msg': '已重新触发图片迁移，后台处理中'})

    @action(methods=['post'], detail=True, url_path='skip_migration')
    def skip_migration(self, request, pk=None):
        """跳过图片迁移：删除剩余 eBay 图片记录，强制标记已完成"""
        base = self.get_object()
        from productbase.tasks import check_has_ebay_images, update_image_migrated_status
        from productbase.models import ProductImage, ProductGroup, ProductCore
        if not check_has_ebay_images(base.id):
            return Response(
                {'msg': '没有需要迁移的 eBay 图片', 'status': 'empty'},
                status=status.HTTP_200_OK)

        group_ids = list(
            ProductGroup.objects.filter(base_id=base.id).values_list('id', flat=True))
        core_ids = list(
            ProductCore.objects.filter(base_id=base.id).values_list('id', flat=True))
        deleted, _ = ProductImage.objects.filter(
            Q(base_group_id=base.id) | Q(group_id__in=group_ids)
            | Q(product_core_id__in=core_ids),
            image_url__contains='ebayimg.com').delete()
        update_image_migrated_status(base.id)
        log_product_action(base, 'IMAGE_MIGRATE',
                           f'跳过图片迁移，删除 {deleted} 张 eBay 图片记录',
                           operator=request.user.username)
        return Response({'msg': f'已跳过，删除 {deleted} 张 eBay 图片'})

    @action(methods=['post'], detail=False, url_path='export_listing')
    def export_listing(self, request):
        """导出店铺上架信息 Excel。传入 ids 导出指定产品（无同步限制），不传则仅导出当前用户未同步的店铺。仅 READY 状态。"""
        ids = request.data.get('ids') if request.data else None
        if ids is not None and (not isinstance(ids, list) or len(ids) == 0):
            return Response({'error': 'ids 必须为非空数组'}, status=400)

        qs = BaseProductGroup.objects.filter(p_status='READY')
        if ids:
            qs = qs.filter(id__in=ids)
        else:
            user_filter = request.user.username if request.user.is_authenticated else 'system'
            qs = qs.filter(creator=user_filter)
        bases = qs.prefetch_related(
            'product_groups__images',
            'product_groups__shop_skus__core_sku__images',
            'product_groups__listing_config')

        # ---- helper ----
        def _val(v, default=''):
            return v if v else default

        def _site_code(site):
            return site.rsplit('_', 1)[-1] if (site and '_' in site) else (site or '')

        def _last_cat(cid):
            return cid.rsplit('|', 1)[-1] if (cid and '|' in cid) else (cid or '')

        def _var_values(shop_sku):
            return '+'.join(p for p in [shop_sku.var1, shop_sku.var2, shop_sku.var3, shop_sku.var4] if p)

        def _variant_name(pg):
            return '+'.join(pg.get_variant_names()) if pg.variant_name else ''

        # ====== pass 1: collect all (base, pg) + global custom keys ======
        all_shops = []
        all_custom_keys = set()
        for base in bases:
            for pg in base.product_groups.all():
                # 未指定 ids 时，仅导出未同步的店铺
                if not ids:
                    synced = (pg.shop_synced_at is not None
                              and pg.updated_at <= pg.shop_synced_at)
                    if synced:
                        continue
                all_shops.append((base, pg))
                all_custom_keys.update((pg.custom_attributes or {}).keys())
        all_custom_keys = sorted(all_custom_keys)
        all_shops.sort(key=lambda x: x[1].id)  # 按创建顺序排序

        if not all_shops:
            return Response({'msg': '没有需要导出的店铺信息', 'status': 'empty'},
                            status=status.HTTP_200_OK)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = '上架信息'
        total_cols = 32 + len(all_custom_keys)  # A-AF(32) + dynamic, B列新增"可售库存"

        # ====== row 1: column headers ======
        row2 = [
            '库存SKU *', '可售库存', '标签', '刊登模板名称 *', '站点 *',
            '通用刊登模板',
            '刊登类目ID *', '刊登类型 *',
            '多属性组合及值', '库存父SKU',
            'eBay账号 *', '平台SKU', '价格 *', '图片 *',
            'UPC', 'EAN', '在线初始库存 *', '标题 *', '详细描述',
            '应用Promoted Listing', 'Promoted Listing广告费率',
            'Campaign', '持续时间 *', '销售计划', '折扣',
            '物品状况',
            '付款方式模板名称 *',
            '货运方式模板名称 *',
            '不运送地区模板名称 *',
            '买家要求模板名称 *',
            '退货政策模板名称 *',
            '物品所在地模板名称 *',
        ]
        for ck in all_custom_keys:
            row2.append(f'{{{ck}}}')
        ws.append(row2)

        # ====== data rows ======
        for base, pg in all_shops:
            lc = pg.listing_config
            has_variants = bool(pg.variant_name and pg.get_variant_names())
            skus = list(pg.shop_skus.all())
            parent_sku = f"{base.supplier}-{base.series}-{base.id}" if base.supplier or base.series else str(base.id)
            default_stock = str(lc.default_stock) if lc else ''

            pl_enabled = lc and lc.promoted_listing_enabled

            # 无变体：把 SKU 信息填入店铺行
            sku_k = sku_l = sku_n = sku_o = ''
            if not has_variants and skus:
                s = skus[0]
                sku_k = s.core_sku.sku
                sku_l = str(float(s.price))
                sku_n = s.core_sku.UPC if s.core_sku.UPC else 'Does not apply'
                sku_o = 'Does not apply'

            shop_row = [
                parent_sku, default_stock, _val(lc.tags if lc else ''), pg.shop_account, _site_code(pg.site),
                _val(lc.listing_template if lc else ''),
                _last_cat(base.category_id),
                '多属性' if has_variants else '固价',
                _variant_name(pg), '',
                pg.shop_account, sku_k, sku_l,
                '\n'.join(img.image_url for img in pg.images.all()),
                sku_n, sku_o, default_stock,
                pg.title, pg.desc or '',
                '应用' if pl_enabled else '',
                str(float(lc.promoted_listing_ad_rate)) if pl_enabled else '',
                lc.campaign if pl_enabled else '',
                'GTC',
                _val(lc.sale_plan if lc else ''),
                _val(lc.discount if lc else ''),
                'New (with tag)',
                _val(lc.payment_method if lc else ''),
                _val(lc.shipping_method if lc else ''),
                _val(lc.excluded_regions if lc else ''),
                _val(lc.buyer_requirements if lc else ''),
                _val(lc.return_policy if lc else ''),
                _val(lc.item_location if lc else ''),
            ]
            for ck in all_custom_keys:
                shop_row.append((pg.custom_attributes or {}).get(ck, ''))
            ws.append(shop_row)

            # SKU rows（仅多属性产品）
            if has_variants:
                for sku in skus:
                    core = sku.core_sku
                    upc = core.UPC if core.UPC else 'Does not apply'
                    sku_row = [
                        '', '', '', '', '', '', '', '',
                        _var_values(sku), parent_sku, '',
                        core.sku, str(float(sku.price)),
                        '\n'.join(img.image_url for img in core.images.all()),
                        upc, 'Does not apply',
                        default_stock,
                        '', '', '', '', '', '', '', '', '', '',
                        '', '', '', '', '',
                    ]
                    for _ in all_custom_keys:
                        sku_row.append('')
                    ws.append(sku_row)

        resp = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        resp['Content-Disposition'] = 'attachment; filename=listing_export.xlsx'
        wb.save(resp)
        # 导出成功后标记已同步（在 save 之后，避免生成失败误标记）
        exported_ids = [pg.id for _, pg in all_shops]
        ProductGroup.objects.filter(id__in=exported_ids).update(
            shop_synced_at=timezone.now())
        # 记录导出日志
        base_shops = {}
        for base, pg in all_shops:
            base_shops.setdefault(base, []).append(pg.id)
        for base, pg_list in base_shops.items():
            log_product_action(base, 'EXPORT_LISTING',
                               f'导出 {len(pg_list)} 个店铺',
                               operator=request.user.username)
        return resp


class ProductGroupViewSet(mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """
    店铺产品组接口：查看 / 修改 / 删除店铺。
    DELETE 会级联删除该店铺下所有 ProductShop，不影响 ProductCore。
    """
    serializer_class = ProductGroupSerializer
    queryset = ProductGroup.objects.prefetch_related(
        "shop_skus__core_sku__images", "images").all()

    def perform_destroy(self, instance):
        log_product_action(instance.base, 'DELETE_SHOP',
                           f'删除店铺: {instance.shop_account} ({instance.platform})')
        instance.delete()

    def perform_update(self, serializer):
        """修改 variant_name 后仅刷新该店铺的 p_name"""
        instance = serializer.save()
        from productbase.tasks import regenerate_p_names
        regenerate_p_names(instance.base)

    @action(methods=['post'],
            detail=False,
            url_path='optimize')
    def optimize(self, request):
        """调用 Dify AI 优化店铺标题或描述"""
        pg_id = request.data.get('id')
        optimize_type = request.data.get('type')

        if not pg_id or optimize_type not in ('EBAY_TITLE', 'EBAY_DESC'):
            return Response(
                {'error': '请提供 id 和 type（EBAY_TITLE / EBAY_DESC）'},
                status=400)

        from productbase.dify import optimize_product_text, record_dify_usage
        from productbase.models import ProductGroup

        try:
            pg = ProductGroup.objects.select_related('base').get(id=pg_id)
        except ProductGroup.DoesNotExist:
            return Response({'error': f'店铺不存在: id={pg_id}'}, status=404)

        result, usage, error = optimize_product_text(pg_id, optimize_type,
                                                     user=request.user)
        if error:
            return Response({'error': error}, status=500)

        # 记录消耗
        record_dify_usage(request.user, pg, optimize_type, usage)

        # 标记优化状态
        if optimize_type == 'EBAY_TITLE':
            pg.title_optimized = True
            pg.save(update_fields=['title_optimized'])
            log_action = 'OPTIMIZE_TITLE'
            log_detail = (f'优化店铺 {pg.shop_account} 标题：'
                          f'{usage.get("total_tokens", 0)} tokens, '
                          f'¥{usage.get("total_price", "0")}')
        else:
            pg.desc_optimized = True
            pg.save(update_fields=['desc_optimized'])
            log_action = 'OPTIMIZE_DESC'
            log_detail = (f'优化店铺 {pg.shop_account} 描述：'
                          f'{usage.get("total_tokens", 0)} tokens, '
                          f'¥{usage.get("total_price", "0")}')

        log_product_action(pg.base, log_action, log_detail,
                           operator=request.user.username)

        return Response({
            'id': result['id'],
            optimize_type.lower().replace('ebay_', ''): result.get(
                'title', result.get('desc', '')),
            'usage': {
                'total_tokens': usage.get('total_tokens', 0),
                'total_price': str(usage.get('total_price', '0')),
            },
        })


class SupplierViewSet(viewsets.ModelViewSet):
    """供应商 CRUD"""
    serializer_class = SupplierSerializer
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filter_fields = ('is_favorite', )
    search_fields = ('name', 'contact_person', 'phone')
    ordering_fields = ('create_time', 'name')

    queryset = Supplier.objects.prefetch_related('series_list').all()

    @action(methods=['get'], detail=False, url_path='quick_list')
    def quick_list(self, request):
        """轻量供应商列表：仅 id/name/is_favorite + 内联系列，收藏排前面"""
        search = request.query_params.get('search', '').strip()
        qs = Supplier.objects.prefetch_related('series_list')
        if search:
            qs = qs.filter(name__icontains=search)
        qs = qs.order_by('-is_favorite', 'name')

        result = [{
            'id': s.id,
            'name': s.name,
            'is_favorite': s.is_favorite,
            'series': [
                {'id': ser.id, 'name': ser.name, 'price': float(ser.price)}
                for ser in s.series_list.all()
            ]
        } for s in qs]

        return Response(result)


class ProductSeriesViewSet(viewsets.ModelViewSet):
    """产品系列 CRUD"""
    serializer_class = ProductSeriesSerializer
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filter_fields = ('supplier', )
    search_fields = ('name', )
    ordering_fields = ('create_time', 'name')

    queryset = ProductSeries.objects.select_related('supplier').all()


class ProductLogViewSet(viewsets.ReadOnlyModelViewSet):
    """产品操作日志（只读）"""
    serializer_class = ProductLogSerializer
    pagination_class = DefaultPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filter_fields = ('base_group', 'action', 'operator')
    ordering_fields = ('create_time', )

    queryset = ProductLog.objects.select_related('base_group').all()


# ------------------------------------------------------------------------------
# 用户自定义配置 ViewSets
# ------------------------------------------------------------------------------

class ShopConfigViewSet(viewsets.ModelViewSet):
    """店铺配置 CRUD"""
    serializer_class = ShopConfigSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filter_fields = ('platform', 'is_main', 'shop_account', 'site', 'user')
    search_fields = ('shop_account', 'site')
    ordering_fields = ('create_time', )

    def get_queryset(self):
        qs = ShopConfig.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        from django.db import IntegrityError
        user = self.request.user
        # 第一个店铺配置：强制设为 主店铺 + 自动创建
        is_first = not ShopConfig.objects.filter(user=user).exists()
        if is_first:
            serializer.validated_data['is_main'] = True
            serializer.validated_data['auto_create_shop'] = True
        else:
            is_main = serializer.validated_data.get('is_main', False)
            if is_main:
                ShopConfig.objects.filter(user=user, is_main=True).update(
                    is_main=False)
        try:
            serializer.save(user=user, creator=user)
        except IntegrityError:
            raise ValidationError(
                '该平台、账号、站点的店铺配置已存在')

    def perform_update(self, serializer):
        instance = serializer.instance
        user = self.request.user
        is_main = serializer.validated_data.get('is_main', instance.is_main)
        auto_create = serializer.validated_data.get(
            'auto_create_shop', instance.auto_create_shop)

        # 设为 主店铺 时强制 auto_create_shop=True
        if is_main:
            serializer.validated_data['auto_create_shop'] = True

        # 不允许取消最后一个 主+自动创建 的店铺
        if instance.is_main and instance.auto_create_shop:
            other_main = ShopConfig.objects.filter(
                user=user, is_main=True, auto_create_shop=True).exclude(
                    pk=instance.pk).exists()
            if not other_main:
                if not is_main:
                    raise ValidationError('必须保留至少一个主店铺')
                if not auto_create:
                    raise ValidationError('主店铺的自动创建不能关闭')

        if is_main:
            # 关闭该用户其他主店铺（排除自身）
            ShopConfig.objects.filter(user=user, is_main=True).exclude(
                pk=instance.pk).update(is_main=False)
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()


class ListingConfigFilter(FilterSet):
    """match_shop_account / match_site 支持逗号分隔的多值 OR 查询"""
    match_shop_account = CharFilter(method='filter_multi_or')
    match_site = CharFilter(method='filter_multi_or')

    def filter_multi_or(self, qs, name, value):
        values = [v.strip() for v in value.split(',') if v.strip()]
        if not values:
            return qs
        q = Q()
        for v in values:
            if v == '__empty__':
                q |= Q(**{f'{name}': ''}) | Q(**{f'{name}__isnull': True})
            else:
                q |= Q(**{f'{name}__icontains': v})
        return qs.filter(q)

    class Meta:
        model = ListingConfig
        fields = ['user']


class ListingConfigViewSet(viewsets.ModelViewSet):
    """刊登配置 CRUD"""
    serializer_class = ListingConfigSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filterset_class = ListingConfigFilter
    search_fields = ('name', )
    ordering_fields = ('create_time', 'name')

    def get_queryset(self):
        qs = ListingConfig.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, creator=self.request.user)

    def perform_destroy(self, instance):
        shop_linked = instance.shop_configs.count()
        pg_linked = instance.linked_product_groups.count()
        errors = []
        if shop_linked > 0:
            errors.append(f'{shop_linked} 个店铺配置')
        if pg_linked > 0:
            errors.append(f'{pg_linked} 个产品店铺')
        if errors:
            raise ValidationError(
                f'该刊登配置已被 {"、".join(errors)} 引用，无法删除。')
        instance.delete()


class FetchConfigViewSet(viewsets.ModelViewSet):
    """抓取配置 CRUD"""
    serializer_class = FetchConfigSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filter_fields = ('user', 'is_active')
    search_fields = ('name', )
    ordering_fields = ('create_time', 'name')

    def get_queryset(self):
        qs = FetchConfig.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        is_active = serializer.validated_data.get('is_active', False)
        if is_active:
            # 关闭该用户所有其他启用的配置
            FetchConfig.objects.filter(user=user, is_active=True).update(
                is_active=False)
        serializer.save(user=user, creator=user)

    def perform_update(self, serializer):
        user = self.request.user
        is_active = serializer.validated_data.get('is_active', False)
        if is_active:
            # 关闭该用户所有其他启用的配置（排除自身）
            FetchConfig.objects.filter(user=user, is_active=True).exclude(
                pk=serializer.instance.pk).update(is_active=False)
        serializer.save()

    @action(methods=['post'], detail=True, url_path='activate')
    def activate(self, request, pk=None):
        """启用指定抓取配置（关闭其他）"""
        config = self.get_object()
        FetchConfig.objects.filter(user=request.user, is_active=True).exclude(
            pk=config.pk).update(is_active=False)
        config.is_active = True
        config.save(update_fields=['is_active'])
        return Response({'status': 'success', 'msg': f'已启用: {config.name}'})


class StatsViewSet(viewsets.ViewSet):
    """工作统计仪表盘"""
    permission_classes = [IsAuthenticated]

    def list(self, request):
        from datetime import datetime
        from django.contrib.auth import get_user_model
        from django.db.models import Count

        User = get_user_model()
        start = request.query_params.get('start_date')
        end = request.query_params.get('end_date')

        try:
            start_dt = datetime.strptime(start, '%Y-%m-%d') if start else None
            end_dt = datetime.strptime(
                end, '%Y-%m-%d').replace(hour=23, minute=59, second=59
                                         ) if end else None
        except (ValueError, TypeError):
            return Response({'error': '日期格式需为 YYYY-MM-DD'}, status=400)

        # 确定查询用户范围（管理员只看 STAFF 且激活的用户）
        if request.user.is_superuser:
            users = User.objects.filter(last_name='STAFF', is_active=True)
        else:
            users = User.objects.filter(username=request.user.username)

        time_filter = {}
        if start_dt:
            time_filter['create_time__gte'] = start_dt
        if end_dt:
            time_filter['create_time__lte'] = end_dt

        result = []
        for user in users:
            uname = user.username
            utime = dict(time_filter)

            # 抓取产品：BaseProductGroup 按 create_time
            products = BaseProductGroup.objects.filter(
                creator=uname, **utime).count()

            # 创建店铺/变体：从 ProductLog 统计
            log_filter = dict(time_filter)
            shops = ProductLog.objects.filter(
                action='ADD_SHOP', operator=uname, **log_filter).count()
            skus = ProductLog.objects.filter(
                action='VARIANT', operator=uname, **log_filter).count()

            # 导出统计：用 synced_at 时间戳直接计独立店铺/SKU 数
            shop_qs = ProductGroup.objects.filter(base__creator=uname)
            sku_qs = ProductCore.objects.filter(base__creator=uname)
            if start_dt:
                shop_qs = shop_qs.filter(shop_synced_at__gte=start_dt)
                sku_qs = sku_qs.filter(sku_synced_at__gte=start_dt)
            if end_dt:
                shop_qs = shop_qs.filter(shop_synced_at__lte=end_dt)
                sku_qs = sku_qs.filter(sku_synced_at__lte=end_dt)
            shops_exported = shop_qs.count()
            skus_exported = sku_qs.count()

            # Dify AI 消耗统计
            dify_qs = DifyUsageLog.objects.filter(user=user)
            if start_dt:
                dify_qs = dify_qs.filter(create_time__gte=start_dt)
            if end_dt:
                dify_qs = dify_qs.filter(create_time__lte=end_dt)
            dify_agg = dify_qs.aggregate(
                total_tokens=Sum('total_tokens'),
                total_cost=Sum('total_price'))

            result.append({
                'username': uname,
                'display_name': user.first_name or uname,
                'stats': {
                    'products_fetched': products,
                    'shops_created': shops,
                    'skus_created': skus,
                    'shops_exported': shops_exported,
                    'skus_exported': skus_exported,
                    'dify_tokens': dify_agg['total_tokens'] or 0,
                    'dify_cost': str(dify_agg['total_cost'] or 0),
                }
            })

        return Response({
            'period': {'start': start, 'end': end},
            'users': result,
        })


class PricingRuleViewSet(viewsets.ModelViewSet):
    """定价规则 CRUD"""
    serializer_class = PricingRuleSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    filter_fields = ('user',)
    search_fields = ('name', )
    ordering_fields = ('create_time', 'name')

    def get_queryset(self):
        qs = PricingRule.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, creator=self.request.user)

    def perform_destroy(self, instance):
        linked = instance.shop_configs.count()
        if linked > 0:
            raise ValidationError(
                f'该定价规则已被 {linked} 个店铺配置引用，无法删除。')
        instance.delete()

    @action(methods=['post'], detail=False, url_path='test_pricing')
    def test_pricing(self, request):
        """测试定价：传入 formula/min_price/max_price/price，返回计算结果"""
        from productbase.tasks import validate_formula, apply_pricing_rule

        formula = (request.data.get('formula') or '').strip()
        price = request.data.get('price')

        if not formula:
            return Response({'error': 'formula 不能为空'}, status=400)
        try:
            price = float(price)
        except (TypeError, ValueError):
            return Response({'error': 'price 必须是有效数字'}, status=400)

        # 验证公式
        is_valid, err = validate_formula(formula)
        if not is_valid:
            return Response({'error': f'公式无效: {err}'}, status=400)

        # 构造临时 PricingRule 用于计算
        min_price = request.data.get('min_price')
        max_price = request.data.get('max_price')
        try:
            min_price = float(min_price) if min_price not in (None, '') else None
        except (TypeError, ValueError):
            min_price = None
        try:
            max_price = float(max_price) if max_price not in (None, '') else None
        except (TypeError, ValueError):
            max_price = None

        tmp_rule = PricingRule(
            formula=formula,
            min_price=min_price,
            max_price=max_price,
            name='test')

        final_price, log_detail = apply_pricing_rule(price, tmp_rule)

        # 计算目标价（不限价时的结果）
        from productbase.tasks import evaluate_formula
        target = evaluate_formula(formula, price=price)

        return Response({
            'original_price': price,
            'target_price': round(target, 2),
            'final_price': round(final_price, 2),
            'min_price': min_price,
            'max_price': max_price,
            'detail': log_detail,
        })


class VariantMappingAttributeViewSet(viewsets.ModelViewSet):
    """变体映射 CRUD — 所有用户共享，无需按用户隔离"""
    serializer_class = VariantMappingAttributeSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    search_fields = ('attribute_name',)
    ordering_fields = ('attribute_name', 'create_time')

    def get_queryset(self):
        return VariantMappingAttribute.objects.prefetch_related('values').all()

    def perform_create(self, serializer):
        attr = serializer.save()
        OperateLog.objects.create(
            op_type='PRODUCT',
            op_log=f'新增变体映射属性: {attr.attribute_name}',
            target_id=attr.id,
            user=self.request.user)

    def perform_update(self, serializer):
        attr = serializer.save()
        OperateLog.objects.create(
            op_type='PRODUCT',
            op_log=f'更新变体映射属性: {attr.attribute_name}',
            target_id=attr.id,
            user=self.request.user)

    def perform_destroy(self, instance):
        OperateLog.objects.create(
            op_type='PRODUCT',
            op_log=f'删除变体映射属性: {instance.attribute_name}',
            target_id=instance.id,
            user=self.request.user)
        instance.delete()

    @action(methods=['post'], detail=False, url_path='preview')
    def preview(self, request):
        """预览映射效果：传入 variant_keys 和各维度值列表，返回 var_mappings 增量"""
        variant_keys = request.data.get('variant_keys', [])
        var_values_by_dim = request.data.get('var_values_by_dim', None)

        if not isinstance(variant_keys, list):
            return Response({'error': 'variant_keys 必须是数组'}, status=400)

        variant_keys = [k.strip().lower() for k in variant_keys]

        # 支持两种输入模式：
        # 1. var_values_by_dim: {"colour": ["Black","Blue"], "model": ["For Samsung A16"]}
        # 2. var_values 数组（旧模式，兼容）
        if var_values_by_dim and isinstance(var_values_by_dim, dict):
            var_values_by_dim = {
                k.strip().lower(): v
                for k, v in var_values_by_dim.items()
                if isinstance(v, list)
            }
        else:
            var_values = request.data.get('var_values', [])
            if not isinstance(var_values, list):
                return Response(
                    {'error': 'var_values_by_dim 或 var_values 需要为数组'},
                    status=400)
            var_values_by_dim = {}
            for i, vk in enumerate(variant_keys):
                if i < len(var_values) and var_values[i]:
                    var_values_by_dim[vk] = [var_values[i]]

        from productbase.tasks import build_var_mappings_from_config
        result = build_var_mappings_from_config(var_values_by_dim)

        # 整理变更明细
        changes = []
        for dim, mapping in result.items():
            for original, mapped in mapping.items():
                changes.append({
                    'dimension': dim,
                    'original': original,
                    'mapped': mapped,
                })

        return Response({
            'var_mappings': result,
            'changes': changes,
        })

    @action(methods=['post'], detail=True, url_path='reorder')
    def reorder(self, request, pk=None):
        """拖拽排序：传入 value ID 列表，按顺序分配优先级（越靠前优先级越高）"""
        attr = self.get_object()
        value_ids = request.data.get('value_ids', [])

        if not isinstance(value_ids, list) or not value_ids:
            return Response(
                {'error': 'value_ids 必须是非空数组'}, status=400)

        from productbase.models import VariantMappingValue
        # 只接受该属性下的 value
        values = {
            v.id: v
            for v in VariantMappingValue.objects.filter(attribute=attr)
        }

        if len(value_ids) != len(values):
            return Response(
                {'error': f'value_ids 数量({len(value_ids)})与属性下实际值数量({len(values)})不一致'},
                status=400)

        # 按提交顺序分配优先级：列表越靠前 priority 越高
        max_priority = len(value_ids)
        for val_id in value_ids:
            if val_id not in values:
                return Response(
                    {'error': f'value {val_id} 不属于该属性'}, status=400)
            values[val_id].priority = max_priority
            max_priority -= 1
            values[val_id].save(update_fields=['priority'])

        return Response({
            'status': 'success',
            'msg': f'已更新 {len(value_ids)} 个匹配值的优先级',
        })


class WarehouseConfigViewSet(viewsets.ModelViewSet):
    """仓库匹配配置 CRUD — 所有用户共享"""
    serializer_class = WarehouseConfigSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)
    search_fields = ('category_id', 'category_name', 'warehouse')
    ordering_fields = ('priority', 'create_time')

    def get_queryset(self):
        return WarehouseConfig.objects.all()

    def perform_create(self, serializer):
        config = serializer.save()
        label = config.category_id or config.category_name or '默认'
        OperateLog.objects.create(
            op_type='PRODUCT',
            op_log=f'新增仓库匹配规则: {label} → {config.warehouse}',
            target_id=config.id,
            user=self.request.user)

    def perform_update(self, serializer):
        config = serializer.save()
        label = config.category_id or config.category_name or '默认'
        OperateLog.objects.create(
            op_type='PRODUCT',
            op_log=f'更新仓库匹配规则: {label} → {config.warehouse}',
            target_id=config.id,
            user=self.request.user)

    def perform_destroy(self, instance):
        label = instance.category_id or instance.category_name or '默认'
        OperateLog.objects.create(
            op_type='PRODUCT',
            op_log=f'删除仓库匹配规则: {label} → {instance.warehouse}',
            target_id=instance.id,
            user=self.request.user)
        instance.delete()
