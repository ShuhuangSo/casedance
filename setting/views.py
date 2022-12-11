from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

from .models import Tag, OperateLog, Menu, SysRefill
from .serializers import TagSerializer, OperateLogSerializer, MenuSerializer, UserSerializer, ALLMenuSerializer, \
    UserMenuSerializer, SysRefillSerializer
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

    @action(methods=['post'], detail=False, url_path='create_tag')
    def create_tag(self, request):
        user = self.request.user
        tag_name = request.data['tag_name']
        tag_type = request.data['type']
        color = request.data['color']

        is_exist = Tag.objects.filter(user=user, type=tag_type, tag_name=tag_name).count()
        if is_exist:
            return Response({'msg': '标签名称已存在！'}, status=status.HTTP_202_ACCEPTED)
        tag = Tag()
        tag.tag_name = tag_name
        tag.type = tag_type
        tag.color = color
        tag.user = user
        tag.save()
        return Response({'msg': '创建成功'}, status=status.HTTP_200_OK)


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


class AllMenuViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    """
    list:
        全部前端导航菜单列表
    """
    queryset = Menu.objects.all()
    serializer_class = ALLMenuSerializer  # 序列化

    def get_queryset(self):
        # 返回admin用户数据
        user = User.objects.get(username='admin')
        return Menu.objects.filter(user=user, parent=None)


class UserMenuViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    """
    list:
        指定用户前端导航菜单列表
    """
    queryset = Menu.objects.all()
    serializer_class = UserMenuSerializer  # 序列化

    def get_queryset(self):
        user_id = self.request.GET.get("id")
        # 返回指定用户数据
        user = User.objects.get(id=user_id)
        return Menu.objects.filter(user=user, parent=None)

    @action(methods=['post'], detail=True, url_path='create_menu')
    def create_user_menu(self, request, pk):
        user = User.objects.get(id=pk)
        admin = User.objects.get(username='admin')
        queryset = Menu.objects.filter(user=admin)

        user_count = Menu.objects.filter(user=user).count()
        admin_count = Menu.objects.filter(user=admin).count()
        menu_set = Menu.objects.filter(user=user)
        # 如果菜单数量与admin相同，说明是修改
        if user_count == admin_count:
            menu_set.update(is_active=False)
            p_ids = []
            for i in menu_set:
                for item in queryset:
                    if item.id in request.data:
                        if item.name == i.name:
                            i.is_active = True
                            i.save()
                            if not i.id in p_ids:
                                if i.parent:
                                    p_ids.append(i.parent.id)

            # 如果有子菜单，父菜单设为true
            for i in p_ids:
                m = Menu.objects.get(id=i)
                m.is_active = True
                m.save()

            return Response({'msg': '修改成功'}, status=status.HTTP_200_OK)

        # 如果是部分菜单新增，则先全部删除，再新增
        if admin_count != user_count and user_count > 0:
            us = Menu.objects.filter(user=user)
            for i in us:
                if i.parent:
                    i.delete()
            Menu.objects.filter(user=user).delete()

        # 先创建父菜单
        parent_add_list = []
        for i in queryset:
            if not i.parent:
                parent_add_list.append(
                    Menu(
                        parent=i.parent,
                        path=i.path,
                        component=i.component,
                        name=i.name,
                        icon=i.icon,
                        order_num=i.order_num,
                        user=user,
                        is_active=False
                    )
                )
        Menu.objects.bulk_create(parent_add_list)

        # 创建子菜单
        qt = Menu.objects.filter(user=user)
        children_add_list = []

        for i in qt:
            for item in queryset:
                if item.parent:
                    if item.parent.name == i.name:
                        children_add_list.append(
                            Menu(
                                parent=i,
                                path=item.path,
                                component=item.component,
                                name=item.name,
                                icon=item.icon,
                                order_num=item.order_num,
                                user=user,
                                is_active=True if item.id in request.data else False
                            )
                        )
                        i.is_active = True
                        i.save()
        Menu.objects.bulk_create(children_add_list)

        return Response({'msg': '创建成功'}, status=status.HTTP_200_OK)


class UserViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    """
    list:
        user信息
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer  # 序列化

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)  # 过滤,搜索
    filter_fields = ('is_staff', 'is_active', 'is_superuser', 'last_name')  # 配置过滤字段
    search_fields = ('username', 'first_name')  # 配置搜索字段

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
        info.update({'id': user.id})

        return Response(info, status=status.HTTP_200_OK)

    # 注册用户
    @action(methods=['post'], detail=False, url_path='create_user')
    def create_user(self, request):
        username = request.data['username']
        password = request.data['password']
        first_name = request.data['first_name']
        last_name = request.data['last_name']
        email = request.data['email']
        is_superuser = request.data['is_superuser']

        is_exist = User.objects.filter(username=username).count()
        if is_exist:
            return Response({'msg': '手机号已存在!', 'success': False}, status=status.HTTP_202_ACCEPTED)

        user = User()
        user.username = username
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.is_superuser = is_superuser
        user.save()

        return Response({'msg': '创建成功!', 'success': True, 'id': user.id, 'name': user.first_name},
                        status=status.HTTP_200_OK)

    # 修改用户资料
    @action(methods=['put'], detail=False, url_path='edit_user')
    def edit_user(self, request):
        u_id = request.data['id']
        first_name = request.data['first_name']
        password = request.data['password']
        last_name = request.data['last_name']
        email = request.data['email']
        is_superuser = request.data['is_superuser']
        is_active = request.data['is_active']

        user = User.objects.get(id=u_id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.is_superuser = is_superuser
        user.is_active = is_active
        if password:
            user.set_password(password)
        user.save()
        return Response({'msg': '修改成功!'}, status=status.HTTP_200_OK)


class SysRefillViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    """
    list:
        补货推荐设置列表
    """
    queryset = SysRefill.objects.all()
    serializer_class = SysRefillSerializer  # 序列化

