from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import Tag
from .serializers import TagSerializer


# Create your views here.
class DefaultPagination(PageNumberPagination):
    """
    分页设置
    """
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class TagViewSet(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """
    list:
        标签库,分页,过滤,搜索,排序
    create:
        标签库新增
    retrieve:
        标签库详情页
    update:
        标签库修改
    destroy:
        标签库删除
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)  # 过滤,搜索,排序
    filter_fields = ('type', 'color', 'user')  # 配置过滤字段
    search_fields = ('tag_name',)  # 配置搜索字段
