import time
from random import Random

from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.
from sale.models import CustomerDiscount, Customer, CustomerTag
from sale.serializers import CustomerDiscountSerializer, CustomerSerializer, CustomerTagSerializer


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
