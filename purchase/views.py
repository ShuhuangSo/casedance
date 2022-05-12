import time
from random import Random

from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.db.models import Q

from product.models import Product, Supplier
from .models import PurchaseOrder, PurchaseDetail, PurchaseOrderTag, PostInfo, RefillPromote
from .serializers import PurchaseOrderSerializer, PurchaseDetailSerializer, PurchaseOrderTagSerializer, \
    RefillPromoteSerializer
from store.models import Store, Stock


# Create your views here.


class DefaultPagination(PageNumberPagination):
    """
    分页设置
    """
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class PurchaseOrderViewSet(mixins.ListModelMixin,
                           mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    """
    list:
        采购单列表,分页,过滤,搜索,排序
    create:
        采购单新增
    retrieve:
        采购单详情页
    update:
        采购单修改
    destroy:
        采购单删除
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = (
        'store', 'supplier', 'user', 'paid_status', 'order_status', 'is_active',
        'purchase_p_tag__tag__tag_name')  # 配置过滤字段
    search_fields = ('p_number',)  # 配置搜索字段
    ordering_fields = ('create_time',)  # 配置排序字段

    # 重写create
    def create(self, request, *args, **kwargs):

        data_status = 'store' in request.data.keys() and 'supplier' in request.data.keys() and 'postage' \
                      in request.data.keys() and 'note' in request.data.keys() and 'purchase_detail' \
                      in request.data.keys() and 'order_status' in request.data.keys()
        if not data_status:
            return Response({'message': '数据错误！'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        data_detail_status = False
        for i in request.data['purchase_detail']:
            data_detail_status = 'qty' in i.keys() and 'unit_cost' in i.keys() and 'product_id' in i.keys() and 'short_note' in i.keys() and 'is_supply_case' in i.keys()
            if not data_detail_status:
                return Response({'message': '数据错误！'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        # 获取不重复批次单号(18位：P+17位数字)
        random_ins = Random()
        p_number = 'P{time_str}{userid}{ranstr}'.format(time_str=time.strftime('%Y%m%d%H%M%S'),
                                                        userid=request.user.id,
                                                        ranstr=random_ins.randint(10, 99))

        # 创建采购单
        store = None
        supplier = None
        if Store.objects.filter(id=request.data['store']):
            store = Store.objects.all().get(id=request.data['store'])
        if Supplier.objects.filter(id=request.data['supplier']):
            supplier = Supplier.objects.all().get(id=request.data['supplier'])
        purchase_order = PurchaseOrder()
        # 判断采购单是直接提交还是放入草稿箱
        if request.data['order_status'] == 'WAIT_CONFIRM':
            purchase_order.order_status = 'WAIT_CONFIRM'
        purchase_order.p_number = p_number
        purchase_order.store = store
        purchase_order.supplier = supplier
        purchase_order.user = request.user
        purchase_order.postage = request.data['postage']
        purchase_order.note = request.data['note']
        purchase_order.rec_name = request.data['rec_name']
        purchase_order.rec_phone = request.data['rec_phone']
        purchase_order.rec_address = request.data['rec_address']
        purchase_order.sup_tips = request.data['sup_tips']
        purchase_order.save()

        # 创建采购单产品详情
        purchase_detail = request.data['purchase_detail']
        if purchase_detail:
            add_list = []
            for i in purchase_detail:
                product = Product.objects.all().get(id=i['product_id'])
                stock = Stock.objects.filter(store=store).get(product=product)
                add_list.append(
                    PurchaseDetail(
                        purchase_order=purchase_order,
                        product=product,
                        unit_cost=i['unit_cost'],
                        qty=i['qty'],
                        is_supply_case=i['is_supply_case'],
                        stock_before=stock.qty,
                        urgent=i['urgent'],
                        short_note=i['short_note']
                    )
                )
            PurchaseDetail.objects.bulk_create(add_list)

        return Response({'id': purchase_order.id}, status=status.HTTP_201_CREATED)

    # test
    @action(methods=['get'], detail=False, url_path='test')
    def test(self, request):
        from . import tasks
        tasks.calc_sold_qty()
        return Response({'msg': 'OK'}, status=status.HTTP_200_OK)

    # 采购单修改，涉及采购商品明细的增加，删除,修改
    @action(methods=['put'], detail=False, url_path='purchase_edit')
    def bulk_edit(self, request):
        operate = 'NO'  # 操作目的
        if 'operate' in request.data.keys():
            operate = request.data['operate']

        p_id = request.data['id']
        store_id = request.data['store']
        supplier_id = request.data['supplier']
        postage = request.data['postage']
        order_status = request.data['order_status']
        note = request.data['note']
        purchase_detail = request.data['purchase_detail']
        inner_case_price = request.data['inner_case_price']
        rec_name = request.data['rec_name']
        rec_phone = request.data['rec_phone']
        rec_address = request.data['rec_address']
        sup_tips = request.data['sup_tips']

        store = Store.objects.get(id=store_id)
        supplier = Supplier.objects.get(id=supplier_id)
        purchase_order = PurchaseOrder.objects.get(id=p_id)
        purchase_order.store = store
        purchase_order.supplier = supplier
        purchase_order.postage = postage
        purchase_order.inner_case_price = inner_case_price
        purchase_order.order_status = order_status
        purchase_order.note = note
        purchase_order.rec_name = rec_name
        purchase_order.rec_phone = rec_phone
        purchase_order.rec_address = rec_address
        purchase_order.sup_tips = sup_tips
        purchase_order.save()

        # 如果是部分发货或者全部发货，记录发货物流信息
        if order_status == 'SENT' or order_status == 'PART_SENT':
            if 'logistic' in request.data.keys():
                logistic = request.data['logistic']
                tracking_number = request.data['tracking_number']
                package_count = request.data['package_count']
                post_info = PostInfo()
                post_info.logistic = logistic
                post_info.tracking_number = tracking_number
                post_info.package_count = package_count
                post_info.purchase_order = purchase_order
                post_info.save()

        add_list = []
        purchase_detail_ids = []
        for i in purchase_detail:
            if 'id' in i.keys():
                purchase_detail_ids.append(i['id'])
                # 有id，证明是修改
                purchase_detail = PurchaseDetail.objects.get(id=i['id'])
                purchase_detail.unit_cost = i['unit_cost']
                purchase_detail.qty = i['qty']
                purchase_detail.is_supply_case = i['is_supply_case']
                purchase_detail.short_note = i['short_note']
                purchase_detail.urgent = i['urgent']
                purchase_detail.paid_qty = i['paid_qty']

                if operate == 'SEND' and purchase_detail.sent_qty < purchase_detail.qty:
                    purchase_detail.sent_qty = i['sent_qty'] + purchase_detail.sent_qty
                if operate == 'SEND' and i['sent_qty'] == purchase_detail.qty:
                    purchase_detail.sent_qty = i['sent_qty']
                if operate == 'RECEIVE' and purchase_detail.received_qty < purchase_detail.qty:
                    purchase_detail.received_qty = i['received_qty'] + purchase_detail.received_qty
                if operate == 'RECEIVE' and i['received_qty'] == purchase_detail.qty:
                    purchase_detail.received_qty = i['received_qty']
                purchase_detail.save()

            else:
                product = Product.objects.all().get(id=i['product_id'])
                stock = Stock.objects.filter(store=store).get(product=product)
                add_list.append(
                    PurchaseDetail(
                        purchase_order=purchase_order,
                        product=product,
                        unit_cost=i['unit_cost'],
                        qty=i['qty'],
                        is_supply_case=i['is_supply_case'],
                        stock_before=stock.qty,
                        urgent=i['urgent'],
                        short_note=i['short_note']
                    )
                )

        queryset = PurchaseDetail.objects.filter(purchase_order=purchase_order)
        # 如果id不存在，证明已被删除
        for i in queryset:
            is_exist = i.id in purchase_detail_ids
            if not is_exist:
                i.delete()

        if add_list:
            PurchaseDetail.objects.bulk_create(add_list)

        # 如果是部分发货或者全部发货，检查收货情况，更改订单状态
        if order_status == 'SENT' or order_status == 'PART_SENT':
            is_full_received = True
            for i in request.data['purchase_detail']:
                pd = PurchaseDetail.objects.get(id=i['id'])
                # 如果有一项收货数量少与采购数量，则订单未完成
                if pd.received_qty < pd.qty:
                    is_full_received = False
                    break
            if is_full_received:
                purchase_order.order_status = 'FINISHED'
                purchase_order.save()

        return Response({'msg': '操作成功'}, status=status.HTTP_200_OK)


class PurchaseDetailViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """
    list:
        采购单详情列表,过滤,排序
    create:
        采购单详情新增
    update:
        采购单详情修改
    retrieve:
        采购单详情
    destroy:
        采购单详情删除
    """
    queryset = PurchaseDetail.objects.all()
    serializer_class = PurchaseDetailSerializer  # 序列化

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('purchase_order',)  # 配置过滤字段
    ordering_fields = ('create_time',)  # 配置排序字段


class PurchaseOrderTagViewSet(mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet):
    """
    list:
        采购单标签,分页,过滤,搜索,排序
    create:
        采购单标签新增
    retrieve:
        采购单标签详情页
    update:
        采购单标签修改
    destroy:
        采购单标签删除
    """
    queryset = PurchaseOrderTag.objects.all()
    serializer_class = PurchaseOrderTagSerializer  # 序列化

    filter_backends = (DjangoFilterBackend,)  # 过滤
    filter_fields = ('purchase_order', 'tag',)  # 配置过滤字段


class RefillPromoteViewSet(mixins.ListModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    """
    list:
        采购单标签,分页,过滤,搜索,排序
    """
    queryset = RefillPromote.objects.all()
    serializer_class = RefillPromoteSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序

    search_fields = ('product__sku', 'product__p_name')  # 配置搜索字段
    ordering_fields = ('product__p_name', )  # 配置排序字段

    def get_queryset(self):
        # 返回当前推荐数量大于0的数据
        return RefillPromote.objects.filter(qty__gt=0)

    # 重新计算补货数量
    @action(methods=['get'], detail=False, url_path='re_calc')
    def re_calc(self, request):
        from . import tasks
        tasks.calc_refill()
        return Response({'msg': '完成补货推荐计算'}, status=status.HTTP_200_OK)

    # 生成采购单后重置采购数量为0
    @action(methods=['post'], detail=False, url_path='re_set')
    def re_set(self, request):
        ids = request.data['ids']
        q = Q()
        q.connector = 'OR'
        for i in ids:
            q.children.append(('id', i))
        RefillPromote.objects.filter(q).update(qty=0)
        return Response({'msg': '操作成功'}, status=status.HTTP_200_OK)
