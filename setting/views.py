from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

from .models import Tag, OperateLog, Menu
from .serializers import TagSerializer, OperateLogSerializer, MenuSerializer, UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


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


class OperateLogViewSet(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """
    list:
        操作日志,分页,过滤,搜索,排序
    create:
        操作日志新增
    retrieve:
        操作日志详情页
    update:
        操作日志修改
    destroy:
        操作日志删除
    """
    queryset = OperateLog.objects.all()
    serializer_class = OperateLogSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('op_type', 'target_id', 'user')  # 配置过滤字段
    search_fields = ('op_log',)  # 配置搜索字段
    ordering_fields = ('create_time',)  # 配置排序字段


class MenuViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        前端导航菜单列表
    """
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer  # 序列化

    def get_queryset(self):
        # 返回当前用户数据
        return Menu.objects.filter(user=self.request.user, is_active=True, parent=None)


class UserViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        user信息
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer  # 序列化

    # 获取当前用户信息
    @action(methods=['get'], detail=False, url_path='user_info')
    def get_user_info(self, request):
        user = self.request.user

        info = {}
        info.update({'username': user.username})
        info.update({'name': user.first_name})
        info.update({'role': user.last_name})
        info.update({'email': user.email})
        info.update({'is_superuser': user.is_superuser})

        return Response(info, status=status.HTTP_200_OK)