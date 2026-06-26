from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers
from .models import (BaseProductGroup, ProductGroup, ProductCore, ProductShop,
                     ProductImage, FetchTask, Supplier, ProductSeries,
                     ProductLog, log_product_action,
                     ShopConfig, ListingConfig, FetchConfig, PricingRule)


# 产品图片序列化
class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = ["id", "image_url", "sort", "is_cover"]


# ------------------------------------------------------------------------------
# 核心 SKU 序列化（全局共用数据）
# ------------------------------------------------------------------------------
class ProductCoreSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCore
        fields = ["id", "sku", "p_name", "cost", "UPC", "purchase_url"]


# ------------------------------------------------------------------------------
# 店铺维度 SKU（差异化数据 + 嵌套核心SKU）
# ------------------------------------------------------------------------------
class ProductShopSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # 显式声明，允许嵌套更新时匹配
    core_sku_id = serializers.IntegerField(source="core_sku.id", read_only=True)
    # 把核心SKU数据展开一起返回 → 前端完全不用改
    sku = serializers.CharField(source="core_sku.sku", read_only=True)
    p_name = serializers.CharField(source="core_sku.p_name", read_only=True)
    cost = serializers.DecimalField(source="core_sku.cost",
                                    max_digits=10,
                                    decimal_places=2,
                                    read_only=True)
    UPC = serializers.CharField(source="core_sku.UPC", read_only=True)
    purchase_url = serializers.CharField(source="core_sku.purchase_url",
                                         read_only=True)
    is_synced = serializers.SerializerMethodField()

    def get_is_synced(self, obj):
        return obj.core_sku.sku_synced_at is not None

    # 图片
    images = ProductImageSerializer(many=True,
                                    read_only=True,
                                    source="core_sku.images")

    class Meta:
        model = ProductShop
        fields = [
            "id",
            "core_sku_id",
            "title",
            "sku",
            "p_name",
            "cost",
            "UPC",
            "purchase_url",  # 来自核心SKU
            "price",
            "currency",
            "var1",
            "var2",
            "var3",
            "var4",
            "custom_attributes",
            "images",
            "is_synced",
        ]


# ------------------------------------------------------------------------------
# 店铺产品组（和原来接口完全一样）
# ------------------------------------------------------------------------------
class ShopVariantWriteSerializer(serializers.Serializer):
    """创建店铺时的变体数据 — 用 core_sku_id 标识 SKU"""
    core_sku_id = serializers.IntegerField()
    var1 = serializers.CharField(required=False, allow_blank=True)
    var2 = serializers.CharField(required=False, allow_blank=True)
    var3 = serializers.CharField(required=False, allow_blank=True)
    var4 = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10,
                                     decimal_places=2,
                                     required=False)
    currency = serializers.CharField(required=False)
    title = serializers.CharField(required=False, allow_blank=True)
    custom_attributes = serializers.JSONField(required=False)


class ProductGroupCreateSerializer(serializers.ModelSerializer):
    """用于创建店铺 — shop_account/platform/site 可写，images 可选"""
    images = ProductImageSerializer(many=True, required=False)
    variants = ShopVariantWriteSerializer(many=True, required=False)

    listing_config_id = serializers.PrimaryKeyRelatedField(
        queryset=ListingConfig.objects.all(),
        source="listing_config",
        required=False,
        allow_null=True,
        write_only=True)

    class Meta:
        model = ProductGroup
        fields = [
            "id", "shop_account", "platform", "title", "site",
            "variant_name", "desc", "custom_attributes",
            "images", "variants", "listing_config_id"
        ]

    def create(self, validated_data):
        base = validated_data.pop('base')
        images_data = validated_data.pop('images', None)
        variants_data = validated_data.pop('variants', None)
        validated_data.setdefault('p_status', 'INIT')
        pg = ProductGroup.objects.create(base=base, **validated_data)

        if images_data:
            for img_data in images_data:
                ProductImage.objects.create(group=pg, **img_data)

        # 为所有已有核心 SKU 创建店铺 SKU，并写入传入的变体值
        variants_map = {}
        if variants_data:
            variants_map = {v['core_sku_id']: v for v in variants_data}

        for core in base.core_skus.all():
            var_vals = variants_map.pop(core.id, {})
            ProductShop.objects.create(
                group=pg,
                core_sku=core,
                title=var_vals.get('title', ''),
                price=var_vals.get('price', 0),
                currency=var_vals.get('currency', 'USD'),
                var1=var_vals.get('var1', ''),
                var2=var_vals.get('var2', ''),
                var3=var_vals.get('var3', ''),
                var4=var_vals.get('var4', ''),
                custom_attributes=var_vals.get('custom_attributes'))

        return pg


class ProductGroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # 显式声明，允许嵌套更新时匹配
    variants = ProductShopSerializer(many=True, source="shop_skus", required=False)
    images = ProductImageSerializer(many=True, required=False)
    listing_config_id = serializers.PrimaryKeyRelatedField(
        queryset=ListingConfig.objects.all(),
        source="listing_config",
        required=False,
        allow_null=True,
        write_only=True)
    listing_config_detail = serializers.SerializerMethodField()
    is_synced = serializers.SerializerMethodField()

    def get_is_synced(self, obj):
        return obj.shop_synced_at is not None

    def get_listing_config_detail(self, obj):
        if not obj.listing_config:
            return None
        # 内联返回关键字段，避免循环引用（ListingConfigSerializer 定义在后）
        return {
            "id": obj.listing_config.id,
            "name": obj.listing_config.name,
            "default_stock": obj.listing_config.default_stock,
            "tags": obj.listing_config.tags,
            "item_location": obj.listing_config.item_location,
            "listing_template": obj.listing_config.listing_template,
            "promoted_listing_enabled": obj.listing_config.promoted_listing_enabled,
            "promoted_listing_ad_rate": float(obj.listing_config.promoted_listing_ad_rate),
            "campaign": obj.listing_config.campaign,
            "sale_plan": obj.listing_config.sale_plan,
            "discount": obj.listing_config.discount,
        }

    class Meta:
        model = ProductGroup
        fields = [
            "id", "shop_account", "p_status", "platform", "title", "site",
            "variant_name", "is_main", "desc", "custom_attributes",
            "images", "variants",
            "listing_config_id", "listing_config_detail",
            "is_synced",
        ]
        read_only_fields = ["shop_account", "platform", "site"]

    def update(self, instance, validated_data):
        variants_data = validated_data.pop('shop_skus', None)
        images_data = validated_data.pop('images', None)

        # 仅当有字段实际变更时才重置同步状态
        if any(str(getattr(instance, k, '')) != str(v)
               for k, v in validated_data.items()):
            instance.shop_synced_at = None
        instance = super().update(instance, validated_data)

        # 替换店铺图片：删旧建新，同时关联 base_group
        if images_data is not None:
            instance.images.all().delete()
            for img_data in images_data:
                ProductImage.objects.create(group=instance,
                                            base_group=instance.base,
                                            **img_data)

        if variants_data is not None:
            variant_changed = False
            for var_data in variants_data:
                var_id = var_data.get('id')
                if not var_id:
                    continue
                try:
                    shop_sku = instance.shop_skus.get(id=var_id)
                except ProductShop.DoesNotExist:
                    continue
                for attr, value in var_data.items():
                    if attr != 'id' and getattr(shop_sku, attr) != value:
                        variant_changed = True
                        setattr(shop_sku, attr, value)
                shop_sku.save()
            if variant_changed:
                instance.shop_synced_at = None
                instance.save(update_fields=['shop_synced_at'])

        return instance


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# 核心 SKU 写入序列化器（用于 BaseProductGroup 中 core_skus 增删改）
# ------------------------------------------------------------------------------
class ProductCoreWriteSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    _delete = serializers.BooleanField(default=False, required=False)

    # ProductCore 字段
    sku = serializers.CharField(required=False)
    p_name = serializers.CharField(required=False)
    UPC = serializers.CharField(required=False, allow_blank=True)
    cost = serializers.DecimalField(max_digits=10,
                                    decimal_places=2,
                                    required=False)
    purchase_url = serializers.CharField(required=False, allow_blank=True)

    # ProductShop 同步字段（修改后同步到所有店铺）
    var1 = serializers.CharField(required=False, allow_blank=True)
    var2 = serializers.CharField(required=False, allow_blank=True)
    var3 = serializers.CharField(required=False, allow_blank=True)
    var4 = serializers.CharField(required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10,
                                     decimal_places=2,
                                     required=False)
    currency = serializers.CharField(required=False)

    # SKU 图片（修改时全量替换，新增时随 SKU 创建）
    images = ProductImageSerializer(many=True, required=False)


# ------------------------------------------------------------------------------
# 基础产品组（全局字段 + SKU 管理）
# ------------------------------------------------------------------------------
def _fmt_variant(variant_keys, var1='', var2='', var3='', var4=''):
    """格式化变体值，如 color=Red, size=Large"""
    vals = [var1, var2, var3, var4]
    parts = []
    for i, key in enumerate(variant_keys):
        if i < len(vals) and vals[i]:
            parts.append(f'{key}={vals[i]}')
    return ', '.join(parts) if parts else ''


def _copy_images_by_primary_variant(base, new_core, variant_keys, var_values):
    """
    新增 SKU 时，按主属性值匹配已有 SKU，复制其图片。
    例如主属性=color，新 SKU color=Red → 复制所有 color=Red 的旧 SKU 图片。
    """
    primary = base.primary_variant
    if not primary or primary not in variant_keys:
        return
    dim_idx = variant_keys.index(primary)
    new_val = var_values[dim_idx] if dim_idx < len(var_values) else ''
    if not new_val:
        return

    # 找已有 core：同一 base 下，主属性值相同且有图片
    # var1-4 在 ProductShop 上，通过 shop_records 关联
    field_name = f'shop_records__var{dim_idx + 1}'
    source_cores = ProductCore.objects.filter(
        base=base,
        **{field_name: new_val},
        images__isnull=False
    ).distinct()

    for src in source_cores:
        for img in src.images.all():
            ProductImage.objects.create(
                product_core=new_core,
                group=img.group,
                base_group=img.base_group,
                image_url=img.image_url,
                sort=img.sort,
                is_cover=img.is_cover)
        return  # 只复制第一个有图片的 core


class BaseProductGroupListSerializer(serializers.ModelSerializer):
    """列表专用轻量序列化器，不嵌套 product_groups / core_skus"""
    images = serializers.SerializerMethodField()
    first_product_group_title = serializers.SerializerMethodField()
    image_migration_status = serializers.SerializerMethodField()
    image_migration_summary = serializers.SerializerMethodField()
    # 以下计数字段由 queryset annotate() 预计算，直接声明即可
    sku_count = serializers.IntegerField(read_only=True, default=0)
    group_count = serializers.IntegerField(read_only=True, default=0)
    synced_sku_count = serializers.SerializerMethodField()
    synced_shop_count = serializers.SerializerMethodField()

    def get_images(self, obj):
        main = self._get_main_group(obj)
        if main:
            cover = main.images.filter(is_cover=True).first()
            if cover:
                return cover.image_url
        return ''

    def get_first_product_group_title(self, obj):
        first = obj.product_groups.first()
        return first.title if first else ''

    def get_synced_sku_count(self, obj):
        total = getattr(obj, 'sku_count', 0)
        synced = getattr(obj, '_synced_sku_count', 0)
        return f'{synced}/{total}'

    def get_synced_shop_count(self, obj):
        total = getattr(obj, 'group_count', 0)
        synced = getattr(obj, '_synced_shop_count', 0)
        return f'{synced}/{total}'

    def get_image_migration_status(self, obj):
        if obj.image_migrated:
            return 'done'
        total, ebay = self._get_image_urls(obj)
        if ebay == 0:
            return 'done'
        tried = ProductLog.objects.filter(
            base_group=obj, action='IMAGE_MIGRATE').exists()
        if tried:
            return 'failed' if total == ebay else 'partial'
        return 'pending'

    def get_image_migration_summary(self, obj):
        total, ebay = self._get_image_urls(obj)
        if total == 0:
            return '0/0'
        return f'{total - ebay}/{total}'

    def _get_image_urls(self, obj):
        from productbase.image_hosting import EBAY_IMAGE_DOMAINS
        group_ids = list(ProductGroup.objects.filter(base_id=obj.id).values_list('id', flat=True))
        core_ids = list(ProductCore.objects.filter(base_id=obj.id).values_list('id', flat=True))
        all_urls = ProductImage.objects.filter(
            Q(base_group_id=obj.id) | Q(group_id__in=group_ids)
            | Q(product_core_id__in=core_ids)
        ).values_list('image_url', flat=True)
        urls = list(all_urls)
        total_unique = len(set(urls))
        ebay_unique = len({u for u in urls if any(d in u for d in EBAY_IMAGE_DOMAINS)})
        return total_unique, ebay_unique

    def _get_main_group(self, obj):
        main = obj.product_groups.filter(is_main=True).first()
        if not main:
            main = obj.product_groups.first()
        return main

    class Meta:
        model = BaseProductGroup
        fields = [
            'id', 'p_status', 'category', 'supplier', 'series', 'tag',
            'creator', 'create_time', 'images', 'from_site_id',
            'first_product_group_title',
            'sku_count', 'group_count',
            'synced_sku_count', 'synced_shop_count',
            'image_migration_status', 'image_migration_summary',
            'image_migrated', 'variant_mapped',
        ]


class BaseProductGroupSerializer(serializers.ModelSerializer):
    product_groups = ProductGroupSerializer(many=True, read_only=True)
    core_skus = ProductCoreWriteSerializer(many=True,
                                           required=False,
                                           write_only=True)
    images = serializers.SerializerMethodField()
    creator = serializers.SerializerMethodField()

    def get_images(self, obj):
        """主店铺封面图 URL"""
        main = self._get_main_group(obj)
        if main:
            cover = main.images.filter(is_cover=True).first()
            if cover:
                return cover.image_url
        return ""

    first_product_group_title = serializers.SerializerMethodField()
    sku_count = serializers.SerializerMethodField()
    group_count = serializers.SerializerMethodField()
    synced_sku_count = serializers.SerializerMethodField()
    synced_shop_count = serializers.SerializerMethodField()
    image_migration_status = serializers.SerializerMethodField()
    image_migration_summary = serializers.SerializerMethodField()
    variant_name = serializers.CharField(required=False,
                                          write_only=True,
                                          allow_blank=True)
    main_variant_name = serializers.SerializerMethodField()
    main_variant_list = serializers.SerializerMethodField()
    variant_editor = serializers.SerializerMethodField()

    def get_creator(self, obj):
        User = get_user_model()
        user = User.objects.filter(username=obj.creator).first()
        return user.first_name if user else obj.creator

    def get_first_product_group_title(self, obj):
        first_group = obj.product_groups.first()
        return first_group.title if first_group else ""

    def get_sku_count(self, obj):
        first_group = obj.product_groups.first()
        if not first_group:
            return 0
        return first_group.shop_skus.count()

    def get_group_count(self, obj):
        return obj.product_groups.count()

    def _get_image_urls(self, obj):
        """获取产品下所有唯一图片 URL，返回 (total_unique, ebay_unique)"""
        from productbase.models import ProductImage, ProductGroup, ProductCore
        from productbase.image_hosting import EBAY_IMAGE_DOMAINS
        group_ids = list(ProductGroup.objects.filter(base_id=obj.id).values_list('id', flat=True))
        core_ids = list(ProductCore.objects.filter(base_id=obj.id).values_list('id', flat=True))
        all_urls = ProductImage.objects.filter(
            Q(base_group_id=obj.id) | Q(group_id__in=group_ids)
            | Q(product_core_id__in=core_ids)
        ).values_list('image_url', flat=True)
        urls = list(all_urls)
        total_unique = len(set(urls))
        ebay_unique = len({u for u in urls if any(d in u for d in EBAY_IMAGE_DOMAINS)})
        return total_unique, ebay_unique

    def get_image_migration_status(self, obj):
        """图片迁移状态：done / partial / failed / pending"""
        if obj.image_migrated:
            return 'done'
        total, ebay = self._get_image_urls(obj)
        if ebay == 0:
            return 'done'
        tried = ProductLog.objects.filter(
            base_group=obj, action='IMAGE_MIGRATE').exists()
        if tried:
            if total == ebay:
                return 'failed'
            return 'partial'
        return 'pending'

    def get_image_migration_summary(self, obj):
        """图片迁移摘要：已迁移唯一URL数/需迁移唯一URL总数"""
        total, ebay = self._get_image_urls(obj)
        if total == 0:
            return '0/0'
        return f'{total - ebay}/{total}'

    def get_synced_sku_count(self, obj):
        total = obj.core_skus.count()
        if total == 0:
            return "0/0"
        synced = obj.core_skus.filter(
            sku_synced_at__isnull=False).count()
        return f"{synced}/{total}"

    def get_synced_shop_count(self, obj):
        total = obj.product_groups.count()
        if total == 0:
            return "0/0"
        synced = obj.product_groups.filter(
            shop_synced_at__isnull=False).count()
        return f"{synced}/{total}"

    def _get_main_group(self, obj):
        """获取主店铺：有 is_main=True 的优先，否则取第一个 product_group"""
        main = obj.product_groups.filter(is_main=True).first()
        if not main:
            main = obj.product_groups.first()
        return main

    def get_main_variant_name(self, obj):
        main = self._get_main_group(obj)
        return main.variant_name if main else ""

    def get_main_variant_list(self, obj):
        """
        获取主店铺的变体维度值列表（仅主店铺的 product_group）。
        逻辑与 get_variant_list 一致，但只统计主店铺的 shop_skus。
        """
        main = self._get_main_group(obj)
        if not main or not main.variant_name:
            return {}
        result = {}
        var_map = {0: 'var1', 1: 'var2', 2: 'var3', 3: 'var4'}
        variant_names = main.get_variant_names()
        for i, vname in enumerate(variant_names):
            if i > 3:
                break
            attr = var_map[i]
            values = set()
            for shop_sku in main.shop_skus.all():
                val = getattr(shop_sku, attr, None)
                if val:
                    values.add(val)
            if values:
                result[vname] = sorted(list(values))
        return result

    def get_variant_editor(self, obj):
        """
        合并 main_variant_list 和 var_mappings，返回前端可直接渲染的编辑结构。
        格式: {"color": {"black": "黑色", "Blue": ""}, "model": {...}}
        - key 来自 var_mappings（已有翻译），value 为空字符串（未翻译）
        - main_variant_list 提供所有可用值作为 key，var_mappings 提供已有翻译作为 value
        """
        variant_list = self.get_main_variant_list(obj)
        mappings = obj.var_mappings or {}
        result = {}
        for dim, values in variant_list.items():
            dim_mapping = mappings.get(dim, {})
            result[dim] = {}
            for val in values:
                result[dim][val] = dim_mapping.get(val, "")
        return result

    def update(self, instance, validated_data):
        from productbase.tasks import (generate_unique_sku, generate_p_name,
                                        assign_sku_after_save)

        core_skus_data = validated_data.pop('core_skus', None)
        variant_name = validated_data.pop('variant_name', None)

        # 1. 更新 BaseProductGroup 自身字段
        instance = super().update(instance, validated_data)

        # 1.5 同步 variant_name 到所有店铺
        if variant_name is not None:
            for pg in instance.product_groups.all():
                pg.variant_name = variant_name
                pg.save(update_fields=['variant_name'])

        # 2. 处理核心 SKU 增删改
        if core_skus_data is not None:
            product_groups = list(instance.product_groups.all())
            main_group = self._get_main_group(instance)
            variant_keys = main_group.get_variant_names() if main_group else []
            supplier = instance.supplier
            series = instance.series
            var_mappings = instance.var_mappings or {}

            # 变体维度变更（variant_name 在 ProductGroup 上）
            old_variant_name = main_group.variant_name if main_group else ''

            # 处理前：收集每维度现有值集合
            def _collect_values(variant_keys, base):
                result = {dim: set() for dim in variant_keys}
                for core in ProductCore.objects.filter(base=base).prefetch_related('shop_records'):
                    for shop in core.shop_records.all():
                        for i, dim in enumerate(variant_keys):
                            val = getattr(shop, f'var{i+1}', '')
                            if val:
                                result[dim].add(val)
                return result

            old_values = _collect_values(variant_keys, instance)

            for sku_data in core_skus_data:
                sku_id = sku_data.get('id')
                should_delete = sku_data.get('_delete', False)

                # --- 删除 ---
                if should_delete and sku_id:
                    try:
                        shop = ProductShop.objects.select_related(
                            'core_sku').get(id=sku_id, group__base=instance)
                        shop.core_sku.delete()
                    except ProductShop.DoesNotExist:
                        continue
                    continue

                images_data = sku_data.pop('images', None)

                # 分离 core 字段和 shop 同步字段
                core_field_names = ['sku', 'p_name', 'UPC', 'cost', 'purchase_url']
                shop_field_names = [
                    'var1', 'var2', 'var3', 'var4', 'price', 'currency'
                ]

                core_fields = {
                    k: sku_data[k]
                    for k in core_field_names if k in sku_data
                }
                shop_fields = {
                    k: sku_data[k]
                    for k in shop_field_names if k in sku_data
                }

                if sku_id:
                    # --- 修改 ---
                    # id 是 ProductShop.id（与 GET 响应中 variants[].id 一致）
                    try:
                        shop = ProductShop.objects.select_related(
                            'core_sku').get(id=sku_id, group__base=instance)
                        core = shop.core_sku
                    except ProductShop.DoesNotExist:
                        continue

                    # sku 编码创建后不可修改，避免唯一键冲突
                    core_fields.pop('sku', None)

                    # 仅当有字段实际变更时才重置同步状态（在 setattr 前比较）
                    changed = any(
                        str(getattr(core, k, '')) != str(v)
                        for k, v in core_fields.items())
                    if changed:
                        for k, v in core_fields.items():
                            setattr(core, k, v)
                        core.sku_synced_at = None
                        core.save()

                    # SKU 图片：全量替换（仅关联 product_core，不关联 base_group）
                    if images_data is not None:
                        core.images.all().delete()
                        for img_data in images_data:
                            ProductImage.objects.create(product_core=core,
                                                        **img_data)

                    # 同步 shop_fields 到所有店铺
                    if shop_fields:
                        ProductShop.objects.filter(
                            core_sku=core).update(**shop_fields)
                else:
                    # --- 新增 ---
                    var_values = [
                        shop_fields.get('var1', ''),
                        shop_fields.get('var2', ''),
                        shop_fields.get('var3', ''),
                        shop_fields.get('var4', '')
                    ]
                    p_name = core_fields.get('p_name')
                    if not p_name or p_name == '待分配':
                        p_name = generate_p_name(
                            supplier, series, variant_keys, var_values,
                            var_mappings)

                    new_sku = core_fields.get('sku')
                    if not new_sku or new_sku == '待分配':
                        new_sku = generate_unique_sku()
                    core = ProductCore.objects.create(
                        base=instance,
                        sku=new_sku,
                        p_name=p_name,
                        UPC=core_fields.get('UPC', ''),
                        cost=core_fields.get('cost', 0),
                        purchase_url=core_fields.get('purchase_url', ''))
                    # 如果 SKU 是自动生成的临时值，用自增 ID 回写
                    if not core_fields.get('sku') or core_fields.get(
                            'sku') == '待分配':
                        assign_sku_after_save(core)

                    # 为每个已有店铺创建 ProductShop
                    for pg in product_groups:
                        # 复制该店铺已有 SKU 的价格和币种
                        ref_shop = pg.shop_skus.first()
                        ref_price = ref_shop.price if ref_shop else 0
                        ref_currency = ref_shop.currency if ref_shop else 'USD'
                        ProductShop.objects.create(
                            group=pg,
                            core_sku=core,
                            title='',
                            desc='',
                            price=ref_price,
                            currency=ref_currency,
                            var1=shop_fields.get('var1', ''),
                            var2=shop_fields.get('var2', ''),
                            var3=shop_fields.get('var3', ''),
                            var4=shop_fields.get('var4', ''))

                    # 新增 SKU 图片：前端传入优先，否则按主属性自动复制
                    if images_data:
                        for img_data in images_data:
                            ProductImage.objects.create(product_core=core,
                                                        **img_data)
                    else:
                        _copy_images_by_primary_variant(
                            instance, core, variant_keys, var_values)

            # 处理后：收集每维度最终值集合，对比得出真正增删
            new_values = _collect_values(variant_keys, instance)
            log_parts = []

            # 变体维度变更
            if variant_name is not None and variant_name != old_variant_name:
                old_dims = old_variant_name or '无'
                new_dims = variant_name or '无'
                log_parts.append(f'变体维度: {old_dims} → {new_dims}')

            # 变体值变更（对比处理前后）
            for dim in sorted(set(list(old_values.keys()) + list(new_values.keys()))):
                old_vals = old_values.get(dim, set())
                new_vals = new_values.get(dim, set())
                added = new_vals - old_vals
                removed = old_vals - new_vals
                dim_parts = []
                if added:
                    dim_parts.append(f'新增{",".join(sorted(added))}')
                if removed:
                    dim_parts.append(f'删除{",".join(sorted(removed))}')
                if dim_parts:
                    log_parts.append(f'{dim}: {"; ".join(dim_parts)}')

            if log_parts:
                log_product_action(instance, 'VARIANT',
                                   ' | '.join(log_parts))

        return instance

    class Meta:
        model = BaseProductGroup
        fields = [
            "id", "p_status", "category", "category_id", "supplier", "series", "tag", "note",
            "creator", "create_time", "images", "from_site_id", "from_item_id",
            "first_product_group_title", "sku_count", "group_count",
            "synced_sku_count", "synced_shop_count",
            "image_migration_status", "image_migration_summary",
            "var_mappings", "image_migrated", "variant_mapped", "primary_variant",
            "variant_name", "main_variant_name", "main_variant_list",
            "variant_editor", "core_skus",
            "product_groups"
        ]


# ------------------------------------------------------------------------------
# 抓取任务 序列化器
# ------------------------------------------------------------------------------
class FetchTaskSerializer(serializers.ModelSerializer):
    base_group_id = serializers.IntegerField(source="base_group.id",
                                             read_only=True)
    creator = serializers.SerializerMethodField()

    def get_creator(self, obj):
        User = get_user_model()
        user = User.objects.filter(username=obj.creator).first()
        return user.first_name if user else obj.creator

    class Meta:
        model = FetchTask
        fields = [
            "id", "item_id", "marketplace_id", "platform", "status", "log",
            "base_group_id", "creator", "create_time", "update_time"
        ]
        read_only_fields = fields


# ------------------------------------------------------------------------------
# 供应商 & 产品系列
# ------------------------------------------------------------------------------
class ProductSeriesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductSeries
        fields = [
            "id", "name", "price", "supplier", "create_time"
        ]
        read_only_fields = ["create_time"]


class SupplierSerializer(serializers.ModelSerializer):
    series_list = ProductSeriesSerializer(many=True, read_only=True)

    class Meta:
        model = Supplier
        fields = [
            "id", "name", "is_favorite", "purchase_channel", "link_url",
            "contact_person", "phone", "wechat", "qq", "address",
            "create_time", "series_list"
        ]
        read_only_fields = ["create_time"]


class ProductLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display',
                                           read_only=True)
    base_product_cover = serializers.SerializerMethodField()

    def get_base_product_cover(self, obj):
        """主店铺封面图 URL"""
        if not obj.base_group:
            return ""
        main_group = obj.base_group.product_groups.filter(
            is_main=True).first()
        if not main_group:
            main_group = obj.base_group.product_groups.first()
        if main_group:
            cover = main_group.images.filter(is_cover=True).first()
            if cover:
                return cover.image_url
        return None

    class Meta:
        model = ProductLog
        fields = [
            "id", "base_group", "action", "action_display", "detail",
            "operator", "create_time", "base_product_cover"
        ]


# ------------------------------------------------------------------------------
# 用户自定义配置 序列化器
# ------------------------------------------------------------------------------

class ListingConfigSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()

    def get_creator(self, obj):
        if obj.creator:
            return obj.creator.first_name or obj.creator.username
        return ""

    class Meta:
        model = ListingConfig
        fields = [
            "id", "user", "name", "default_stock", "tags",
            "listing_template", "payment_method", "shipping_method",
            "excluded_regions", "buyer_requirements", "return_policy",
            "item_location",
            "promoted_listing_enabled", "promoted_listing_ad_rate",
            "campaign", "sale_plan", "discount",
            "match_shop_account", "match_site",
            "creator", "create_time"
        ]
        read_only_fields = ["user", "creator", "create_time"]


class PricingRuleSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()

    def get_creator(self, obj):
        if obj.creator:
            return obj.creator.first_name or obj.creator.username
        return ""

    def validate_formula(self, value):
        from productbase.tasks import validate_formula
        is_valid, error = validate_formula(value)
        if not is_valid:
            raise serializers.ValidationError(error)
        return value

    class Meta:
        model = PricingRule
        fields = [
            "id", "user", "name", "formula",
            "min_price", "max_price",
            "creator", "create_time",
        ]
        read_only_fields = ["user", "creator", "create_time"]


class ShopConfigSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()

    def get_creator(self, obj):
        if obj.creator:
            return obj.creator.first_name or obj.creator.username
        return ""

    class Meta:
        model = ShopConfig
        fields = [
            "id", "user", "platform", "shop_account", "site",
            "is_main", "auto_create_shop",
            "listing_config", "pricing_rule",
            "creator", "create_time"
        ]
        read_only_fields = ["user", "creator", "create_time"]


class FetchConfigSerializer(serializers.ModelSerializer):
    creator = serializers.SerializerMethodField()

    def get_creator(self, obj):
        if obj.creator:
            return obj.creator.first_name or obj.creator.username
        return ""

    class Meta:
        model = FetchConfig
        fields = [
            "id", "user", "name", "is_active",
            "keep_attributes", "fixed_attributes",
            "creator", "create_time"
        ]
        read_only_fields = ["user", "creator", "create_time"]
