from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import Store
from .serializers import StoreSerializer

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
