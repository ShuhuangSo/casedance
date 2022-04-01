import time
from random import Random

from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.
from product.models import Product
from sale.models import CustomerDiscount, Customer, CustomerTag, Order, OrderDetail, OrderTag
from sale.serializers import CustomerDiscountSerializer, CustomerSerializer, CustomerTagSerializer, OrderSerializer, \
    OrderDetailSerializer, OrderTagSerializer
from store.models import Store, Stock


class DefaultPagination(PageNumberPagination):
    """
    分页设置
    """
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class CustomerViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    """
    list:
        客户列表,分页,过滤,搜索,排序
    create:
        客户新增
    retrieve:
        客户详情页
    update:
        客户修改
    destroy:
        客户删除
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('pay_way', 'is_active')  # 配置过滤字段
    search_fields = ('company_name', 'customer_code', 'contact_name', 'phone')  # 配置搜索字段
    ordering_fields = ('create_time',)  # 配置排序字段


class CustomerDiscountViewSet(mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet):
    """
    list:
        客户专属优惠列表
    create:
        客户专属优惠新增
    retrieve:
        客户专属优惠详情页
    update:
        客户专属优惠修改
    destroy:
        客户专属优惠删除
    """
    queryset = CustomerDiscount.objects.all()
    serializer_class = CustomerDiscountSerializer  # 序列化

    filter_backends = (DjangoFilterBackend,)  # 过滤
    filter_fields = ('customer', 'p_series', 'discount_type')  # 配置过滤字段


class CustomerTagViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """
    list:
        客户列表,分页,过滤,搜索,排序
    create:
        客户标签新增
    retrieve:
        客户标签详情页
    update:
        客户标签修改
    destroy:
        客户签删除
    """
    queryset = CustomerTag.objects.all()
    serializer_class = CustomerTagSerializer  # 序列化

    filter_backends = (DjangoFilterBackend,)  # 过滤
    filter_fields = ('customer', 'tag',)  # 配置过滤字段


class OrderViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    """
    list:
        销售订单列表,分页,过滤,搜索,排序
    create:
        销售订单新增
    retrieve:
        销售订单详情页
    update:
        销售订单修改
    destroy:
        销售订单删除
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = (
        'store', 'customer', 'user', 'order_type', 'order_status', 'pay_way', 'paid_status', 'is_active')  # 配置过滤字段
    search_fields = ('order_number', 'store', 'customer', 'user')  # 配置搜索字段
    ordering_fields = ('create_time',)  # 配置排序字段

    # 重写create
    def create(self, request, *args, **kwargs):

        data_status = 'store' in request.data.keys() and 'customer' in request.data.keys() \
                      and 'order_type' in request.data.keys() and 'pay_way' in request.data.keys() \
                      and 'address' in request.data.keys() and 'contact_name' in request.data.keys() \
                      and 'phone' in request.data.keys() and 'postage' in request.data.keys() \
                      and 'note' in request.data.keys() and 'mode' in request.data.keys()
        if not data_status:
            return Response({'message': '数据错误！'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        data_detail_status = False
        for i in request.data['order_detail']:
            data_detail_status = 'qty' in i.keys() and 'unit_price' in i.keys() and 'product' in i.keys() and 'sold_price' in i.keys()
            if not data_detail_status:
                return Response({'message': '数据错误！'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        # 获取不重复批次单号(18位：P+17位数字)
        random_ins = Random()
        order_number = 'S{time_str}{userid}{ranstr}'.format(time_str=time.strftime('%Y%m%d%H%M%S'),
                                                            userid=request.user.id,
                                                            ranstr=random_ins.randint(10, 99))

        # 创建销售单
        store = None
        if Store.objects.filter(id=request.data['store']):
            store = Store.objects.all().get(id=request.data['store'])
        if Customer.objects.filter(id=request.data['customer']):
            customer = Customer.objects.all().get(id=request.data['customer'])
        order = Order()
        order.order_number = order_number
        order.store = store
        order.customer = customer
        order.user = request.user
        order.order_type = request.data['order_type']
        order.pay_way = request.data['pay_way']
        order.address = request.data['address']
        order.contact_name = request.data['contact_name']
        order.phone = request.data['phone']
        order.postage = request.data['postage']
        order.note = request.data['note']
        order.mode = request.data['mode']
        order.save()

        # 创建销售单产品明细
        order_detail = request.data['order_detail']
        if order_detail:
            add_list = []
            for i in order_detail:
                product = Product.objects.all().get(id=i['product'])
                stock = Stock.objects.filter(store=store).get(product=product)
                not_enough_stock = False
                # 检查库存是否足够
                if (stock.qty - stock.lock_qty) < i['qty']:
                    not_enough_stock = True
                add_list.append(
                    OrderDetail(
                        order=order,
                        product=product,
                        unit_price=i['unit_price'],
                        qty=i['qty'],
                        sold_price=i['sold_price'],
                    )
                )
            OrderDetail.objects.bulk_create(add_list)
            if not_enough_stock:
                return Response({'message': '库存不足！'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        return Response({'message': '操作成功！'}, status=status.HTTP_201_CREATED)


class OrderDetailViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.GenericViewSet):
    """
    list:
        销售订单明细列表,过滤,排序
    create:
        销售订单明细新增
    update:
        销售订单明细修改
    retrieve:
        销售订单明细详情
    destroy:
        销售订单明细删除
    """
    queryset = OrderDetail.objects.all()
    serializer_class = OrderDetailSerializer  # 序列化

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('order',)  # 配置过滤字段
    ordering_fields = ('create_time',)  # 配置排序字段


class OrderTagViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    """
    list:
        销售订单标签,分页,过滤,搜索,排序
    create:
        销售订单标签新增
    retrieve:
        销售订单签详情页
    update:
        销售订单标签修改
    destroy:
        销售订单标签删除
    """
    queryset = OrderTag.objects.all()
    serializer_class = OrderTagSerializer  # 序列化

    filter_backends = (DjangoFilterBackend,)  # 过滤
    filter_fields = ('order', 'tag',)  # 配置过滤字段
