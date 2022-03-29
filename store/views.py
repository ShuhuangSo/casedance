import time
from random import Random

from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from product.models import Product
from .models import Store, StockInOut, StockInOutDetail, Stock
from .serializers import StoreSerializer, StockInOutSerializer


# Create your views here.


class DefaultPagination(PageNumberPagination):
    """
    分页设置
    """
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class StoreViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """
    list:
        仓库、销售门店列表,分页,过滤,搜索,排序
    create:
        仓库、销售门店新增
    retrieve:
        仓库、销售门店详情页
    update:
        仓库、销售门店修改
    destroy:
        仓库、销售门店删除
    """
    queryset = Store.objects.all()
    serializer_class = StoreSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('type', 'is_active')  # 配置过滤字段
    search_fields = ('store_name', 'contact_name', 'phone')  # 配置搜索字段
    ordering_fields = ('create_time',)  # 配置排序字段


class StockInOutViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """
    list:
        手工出入库/调拨列表,分页,过滤,搜索,排序
    create:
        手工出入库/调拨新增
    retrieve:
        手工出入库/调拨详情页
    update:
        手工出入库/调拨修改
    destroy:
        手工出入库/调拨删除
    """
    queryset = StockInOut.objects.all()
    serializer_class = StockInOutSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = (
    'origin_store', 'target_store', 'user', 'type', 'reason_in', 'reason_out', 'reason_move', 'is_active')  # 配置过滤字段
    search_fields = ('batch_number',)  # 配置搜索字段
    ordering_fields = ('create_time',)  # 配置排序字段

    # 重写create
    def create(self, request, *args, **kwargs):

        # 获取不重复批次单号(18位：M+17位数字)
        random_ins = Random()
        batch_number = 'M{time_str}{userid}{ranstr}'.format(time_str=time.strftime('%Y%m%d%H%M%S'),
                                                            userid=request.user.id,
                                                            ranstr=random_ins.randint(10, 99))
        # 创建出入库单
        origin_store = None
        target_store = None
        if Store.objects.filter(id=request.data['origin_store']):
            origin_store = Store.objects.all().get(id=request.data['origin_store'])
        if Store.objects.filter(id=request.data['target_store']):
            target_store = Store.objects.all().get(id=request.data['target_store'])
        stock_inout = StockInOut()
        stock_inout.batch_number = batch_number
        stock_inout.origin_store = origin_store
        stock_inout.target_store = target_store
        stock_inout.user = request.user
        stock_inout.type = request.data['type']
        stock_inout.reason_in = request.data['reason_in']
        stock_inout.reason_out = request.data['reason_out']
        stock_inout.reason_move = request.data['reason_move']
        stock_inout.save()

        # 创建出入库单产品详情
        inout_detail = request.data['inout_detail']
        if inout_detail:
            add_list = []
            for i in inout_detail:
                product = Product.objects.all().get(id=i['product'])
                stock = Stock.objects.filter(store=target_store).get(product=product)
                add_list.append(
                    StockInOutDetail(
                        stock_in_out=stock_inout,
                        product=product,
                        qty=i['qty'],
                        stock_before=stock.qty
                    )
                )
            StockInOutDetail.objects.bulk_create(add_list)

        # 产品入库操作
        if stock_inout.type == 'IN' and target_store:
            for i in add_list:
                stock = Stock.objects.filter(store=target_store).get(product=i.product)
                stock.qty += i.qty  # 现有库存加上入库库存
                stock.save()

        #  产品出库操作
        if stock_inout.type == 'OUT' and target_store:
            for i in add_list:
                stock = Stock.objects.filter(store=target_store).get(product=i.product)
                stock.qty -= i.qty  # 现有库存减去出库库存
                stock.save()

        #  库存调拨操作
        if stock_inout.type == 'MOVE' and target_store and origin_store:
            for i in add_list:
                ta_stock = Stock.objects.filter(store=target_store).get(product=i.product)
                or_stock = Stock.objects.filter(store=origin_store).get(product=i.product)
                or_stock.qty -= i.qty  # 源仓库减去出库库存
                or_stock.save()
                ta_stock.qty += i.qty  # 目标仓库加上入库库存
                ta_stock.save()

        return Response({'message': '操作成功！'}, status=status.HTTP_201_CREATED)
