import time
from random import Random

from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from product.models import Product, Supplier
from .models import PurchaseOrder, PurchaseDetail, PurchaseOrderTag
from .serializers import PurchaseOrderSerializer, PurchaseDetailSerializer, PurchaseOrderTagSerializer
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
        'store', 'supplier', 'user', 'paid_status', 'order_status', 'is_active')  # 配置过滤字段
    search_fields = ('p_number',)  # 配置搜索字段
    ordering_fields = ('create_time',)  # 配置排序字段

    # 重写create
    def create(self, request, *args, **kwargs):

        data_status = 'store' in request.data.keys() and 'supplier' in request.data.keys() and 'postage' in request.data.keys() and 'note' in request.data.keys() and 'purchase_detail' in request.data.keys()
        if not data_status:
            return Response({'message': '数据错误！'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        data_detail_status = False
        for i in request.data['purchase_detail']:
            data_detail_status = 'qty' in i.keys() and 'unit_cost' in i.keys() and 'product' in i.keys() and 'short_note' in i.keys() and 'is_supply_case' in i.keys()
            if not data_detail_status:
                return Response({'message': '数据错误！'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        # 获取不重复批次单号(18位：P+17位数字)
        random_ins = Random()
        p_number = 'P{time_str}{userid}{ranstr}'.format(time_str=time.strftime('%Y%m%d%H%M%S'),
                                                        userid=request.user.id,
                                                        ranstr=random_ins.randint(10, 99))

        # 创建采购单
        store = None
        if Store.objects.filter(id=request.data['store']):
            store = Store.objects.all().get(id=request.data['store'])
        if Supplier.objects.filter(id=request.data['supplier']):
            supplier = Supplier.objects.all().get(id=request.data['supplier'])
        purchase_order = PurchaseOrder()
        purchase_order.p_number = p_number
        purchase_order.store = store
        purchase_order.supplier = supplier
        purchase_order.user = request.user
        purchase_order.postage = request.data['postage']
        purchase_order.note = request.data['note']
        purchase_order.save()

        # 创建采购单产品详情
        purchase_detail = request.data['purchase_detail']
        if purchase_detail:
            add_list = []
            for i in purchase_detail:
                product = Product.objects.all().get(id=i['product'])
                stock = Stock.objects.filter(store=store).get(product=product)
                add_list.append(
                    PurchaseDetail(
                        purchase_order=purchase_order,
                        product=product,
                        unit_cost=i['unit_cost'],
                        qty=i['qty'],
                        is_supply_case=i['is_supply_case'],
                        stock_before=stock.qty,
                        short_note=i['short_note']
                    )
                )
            PurchaseDetail.objects.bulk_create(add_list)

        return Response({'message': '操作成功！'}, status=status.HTTP_201_CREATED)


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
