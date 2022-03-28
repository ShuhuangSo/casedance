from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, ProductExtraInfo, DeviceModel, CompatibleModel, ProductTag
from .serializers import ProductSerializer, ProductExtraInfoSerializer, DeviceModelSerializer, CompatibleModelSerializer, ProductTagSerializer


# Create your views here.
class DefaultPagination(PageNumberPagination):
    """
    分页设置
    """
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class ProductViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    list:
        产品列表,分页,过滤,搜索,排序
    create:
        产品新增
    retrieve:
        产品详情页
    update:
        产品修改
    destroy:
        产品删除
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('status', 'brand', 'series', 'p_type', 'is_auto_promote', 'stock_strategy')  # 配置过滤字段
    search_fields = ('sku', 'p_name')  # 配置搜索字段
    ordering_fields = ('create_time',)  # 配置排序字段

    #  重写产品删除
    def destroy(self, request, *args, **kwargs):
        print('delete!!')
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductExtraInfoViewSet(mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet):
    """
    list:
        产品附属信息列表,分页,过滤,搜索,排序
    create:
        产品附属信息新增
    retrieve:
        产品附属信息详情页
    update:
        产品附属信息修改
    destroy:
        产品附属信息删除
    """
    queryset = ProductExtraInfo.objects.all()
    serializer_class = ProductExtraInfoSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('type',)  # 配置过滤字段
    search_fields = ('name',)  # 配置搜索字段


class DeviceModelViewSet(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    """
    list:
        市面手机型号表,分页,过滤,搜索,排序
    create:
        市面手机型号表新增
    retrieve:
        市面手机型号表详情页
    update:
        市面手机型号表修改
    destroy:
        市面手机型号表删除
    """
    queryset = DeviceModel.objects.all()
    serializer_class = DeviceModelSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('brand', 'type',)  # 配置过滤字段
    search_fields = ('model',)  # 配置搜索字段


class CompatibleModelViewSet(mixins.ListModelMixin,
                             mixins.CreateModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.DestroyModelMixin,
                             mixins.RetrieveModelMixin,
                             viewsets.GenericViewSet):
    """
    list:
        产品兼容手机型号,分页,过滤,搜索,排序
    create:
        产品兼容手机型号新增
    retrieve:
        产品兼容手机型号详情页
    update:
        产品兼容手机型号修改
    destroy:
        产品兼容手机型号删除
    """
    queryset = CompatibleModel.objects.all()
    serializer_class = CompatibleModelSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)  # 过滤,搜索,排序
    filter_fields = ('product', 'phone_model',)  # 配置过滤字段
    search_fields = ('phone_model',)  # 配置搜索字段


class TagViewSet(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """
    list:
        产品兼容手机型号,分页,过滤,搜索,排序
    create:
        产品兼容手机型号新增
    retrieve:
        产品兼容手机型号详情页
    update:
        产品兼容手机型号修改
    destroy:
        产品兼容手机型号删除
    """
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer  # 序列化

    filter_backends = (DjangoFilterBackend, )  # 过滤
    filter_fields = ('product', 'tag',)  # 配置过滤字段
