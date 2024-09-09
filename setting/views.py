from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action

from .models import Tag, OperateLog, Menu, SysRefill, MLUserPermission
from mercado.models import MLProduct, MLOperateLog, Ship, TransStock
from .serializers import TagSerializer, OperateLogSerializer, MenuSerializer, UserSerializer, ALLMenuSerializer, \
    UserMenuSerializer, SysRefillSerializer, ALLMLUserPermissionSerializer, MLUserPermissionSerializer, \
    MLPermissionSerializer
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


class TagViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                 mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                 mixins.RetrieveModelMixin, viewsets.GenericViewSet):
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
    search_fields = ('tag_name', )  # 配置搜索字段

    @action(methods=['post'], detail=False, url_path='create_tag')
    def create_tag(self, request):
        user = self.request.user
        tag_name = request.data['tag_name']
        tag_type = request.data['type']
        color = request.data['color']

        is_exist = Tag.objects.filter(user=user,
                                      type=tag_type,
                                      tag_name=tag_name).count()
        if is_exist:
            return Response({'msg': '标签名称已存在！'},
                            status=status.HTTP_202_ACCEPTED)
        tag = Tag()
        tag.tag_name = tag_name
        tag.type = tag_type
        tag.color = color
        tag.user = user
        tag.save()
        return Response({'msg': '创建成功'}, status=status.HTTP_200_OK)


class OperateLogViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                        mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                        mixins.RetrieveModelMixin, viewsets.GenericViewSet):
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

    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter)  # 过滤,搜索,排序
    filter_fields = ('op_type', 'target_id', 'user')  # 配置过滤字段
    search_fields = ('op_log', )  # 配置搜索字段
    ordering_fields = ('create_time', )  # 配置排序字段


class MenuViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
        前端导航菜单列表
    """
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer  # 序列化

    def get_queryset(self):
        # 返回当前用户数据
        return Menu.objects.filter(user=self.request.user,
                                   is_active=True,
                                   parent=None)


class AllMenuViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                     mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
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


class UserMenuViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                      mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                      mixins.RetrieveModelMixin, viewsets.GenericViewSet):
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
                    Menu(parent=i.parent,
                         path=i.path,
                         component=i.component,
                         name=i.name,
                         icon=i.icon,
                         order_num=i.order_num,
                         user=user,
                         is_active=False))
        Menu.objects.bulk_create(parent_add_list)

        # 创建子菜单
        qt = Menu.objects.filter(user=user)
        children_add_list = []

        for i in qt:
            for item in queryset:
                if item.parent:
                    if item.parent.name == i.name:
                        children_add_list.append(
                            Menu(parent=i,
                                 path=item.path,
                                 component=item.component,
                                 name=item.name,
                                 icon=item.icon,
                                 order_num=item.order_num,
                                 user=user,
                                 is_active=True
                                 if item.id in request.data else False))
                        i.is_active = True
                        i.save()
        Menu.objects.bulk_create(children_add_list)

        return Response({'msg': '创建成功'}, status=status.HTTP_200_OK)


class AllMLUserPermissionViewSet(mixins.ListModelMixin,
                                 mixins.CreateModelMixin,
                                 mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin,
                                 mixins.RetrieveModelMixin,
                                 viewsets.GenericViewSet):
    """
    list:
        全部美客多操作权限列表
    """
    queryset = MLUserPermission.objects.all()
    serializer_class = ALLMLUserPermissionSerializer  # 序列化

    def get_queryset(self):
        # 返回admin用户数据
        user = User.objects.get(username='admin')
        return MLUserPermission.objects.filter(user=user, parent=None)

    # 归属权转移
    @action(methods=['post'], detail=False, url_path='guishu')
    def guishu(self, request):
        from_id = request.data['from_id']
        target_id = request.data['target_id']

        products = MLProduct.objects.filter(user_id=from_id)
        for i in products:
            i.user_id = target_id
            i.save()
            # 创建操作日志
            log = MLOperateLog()
            log.op_module = 'PRODUCT'
            log.op_type = 'EDIT'
            log.target_type = 'PRODUCT'
            log.target_id = i.id
            log.desc = '转移产品归属权'
            log.user = request.user
            log.save()

        ships = Ship.objects.filter(user_id=from_id)
        for i in ships:
            i.user_id = target_id
            i.save()
            # 创建操作日志
            log = MLOperateLog()
            log.op_module = 'SHIP'
            log.op_type = 'EDIT'
            log.target_type = 'SHIP'
            log.target_id = i.id
            log.desc = '转移运单归属权'
            log.user = request.user
            log.save()

        trans = TransStock.objects.filter(user_id=from_id)
        for i in trans:
            i.user_id = target_id
            i.save()
            # 创建操作日志
            log = MLOperateLog()
            log.op_module = 'TRANS'
            log.op_type = 'EDIT'
            log.target_type = 'TRANS'
            log.target_id = i.id
            log.desc = '转移中转仓产品归属权'
            log.user = request.user
            log.save()
        return Response({'msg': '操作成功!'}, status=status.HTTP_200_OK)

    # 创建默认数据
    @action(methods=['get'], detail=False, url_path='create_default_data')
    def create_default_data(self, request):
        admin = User.objects.get(username='admin')
        MLUserPermission.objects.filter(user=admin,
                                        parent__isnull=False).delete()
        MLUserPermission.objects.filter(user=admin).delete()
        mp = MLUserPermission()
        mp.module_name = '产品库'
        mp.component = 'product'
        mp.order_num = 1
        mp.is_active = True
        mp.user = User.objects.get(username='admin')
        mp.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '包材管理'
        mp_c.component = 'product_packing'
        mp_c.order_num = 1
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '产品导入'
        mp_c.component = 'product_upload'
        mp_c.order_num = 2
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '查看全部产品(不打勾仅能查看自己创建的产品)'
        mp_c.component = 'product_checkAll'
        mp_c.order_num = 3
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '编辑全部产品(不打勾仅能编辑自己创建的产品)'
        mp_c.component = 'product_editAll'
        mp_c.order_num = 4
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '删除全部产品(不打勾仅能删除自己创建的产品)'
        mp_c.component = 'product_deleteAll'
        mp_c.order_num = 5
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '默认查看全部产品'
        mp_c.component = 'product_defaultCheckAll'
        mp_c.order_num = 6
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp = MLUserPermission()
        mp.module_name = '采购管理'
        mp.component = 'purchase'
        mp.order_num = 2
        mp.is_active = True
        mp.user = User.objects.get(username='admin')
        mp.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '查看待采购'
        mp_c.component = 'purchase_checkWaitBuy'
        mp_c.order_num = 1
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '查看已采购'
        mp_c.component = 'purchase_checkAlreadyBuy'
        mp_c.order_num = 2
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '查看已收货'
        mp_c.component = 'purchase_checkReceived'
        mp_c.order_num = 3
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '查看已打包'
        mp_c.component = 'purchase_checkPacked'
        mp_c.order_num = 4
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '查看已出库'
        mp_c.component = 'purchase_checkOut'
        mp_c.order_num = 5
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '新增采购'
        mp_c.component = 'purchase_create'
        mp_c.order_num = 6
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '下单采购'
        mp_c.component = 'purchase_buy'
        mp_c.order_num = 7
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '修改采购价格'
        mp_c.component = 'purchase_changePrice'
        mp_c.order_num = 8
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '确认收货'
        mp_c.component = 'purchase_receive'
        mp_c.order_num = 8
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '产品质检'
        mp_c.component = 'purchase_qc'
        mp_c.order_num = 9
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '确认打包'
        mp_c.component = 'purchase_pack'
        mp_c.order_num = 10
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '数据核查'
        mp_c.component = 'purchase_dataCheck'
        mp_c.order_num = 11
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '产品删除'
        mp_c.component = 'purchase_delete'
        mp_c.order_num = 12
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '数据权限: 查看全部店铺(没打勾仅查看本人店铺)'
        mp_c.component = 'purchase_allShopCheck'
        mp_c.order_num = 13
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp = MLUserPermission()
        mp.module_name = '补货推荐'
        mp.component = 'refill'
        mp.order_num = 3
        mp.is_active = True
        mp.user = User.objects.get(username='admin')
        mp.save()

        mp = MLUserPermission()
        mp.module_name = '运单管理'
        mp.component = 'ship'
        mp.order_num = 3
        mp.is_active = True
        mp.user = User.objects.get(username='admin')
        mp.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '创建运单'
        mp_c.component = 'ship_create'
        mp_c.order_num = 1
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '编辑运单'
        mp_c.component = 'ship_edit'
        mp_c.order_num = 2
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '删除运单'
        mp_c.component = 'ship_delete'
        mp_c.order_num = 3
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '运单导出'
        mp_c.component = 'ship_export'
        mp_c.order_num = 4
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '物流交运'
        mp_c.component = 'ship_carrier_place'
        mp_c.order_num = 4
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '运单打包'
        mp_c.component = 'ship_packing'
        mp_c.order_num = 5
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '费用录入'
        mp_c.component = 'ship_fees'
        mp_c.order_num = 6
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '运单预约'
        mp_c.component = 'ship_book'
        mp_c.order_num = 7
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '运单改约'
        mp_c.component = 'ship_rebook'
        mp_c.order_num = 8
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '操作入仓'
        mp_c.component = 'ship_inwarehouse'
        mp_c.order_num = 9
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '物流结算'
        mp_c.component = 'ship_logi_fee'
        mp_c.order_num = 10
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '附件上传'
        mp_c.component = 'ship_attach_create'
        mp_c.order_num = 11
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '附件删除'
        mp_c.component = 'ship_attach_delete'
        mp_c.order_num = 12
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '数据权限: 查看全部店铺(没打勾仅查看本人店铺)'
        mp_c.component = 'ship_allShopCheck'
        mp_c.order_num = 13
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp = MLUserPermission()
        mp.module_name = 'FBM库存'
        mp.component = 'fbmStock'
        mp.order_num = 4
        mp.is_active = True
        mp.user = User.objects.get(username='admin')
        mp.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '店铺数据'
        mp_c.component = 'fbmStock_shopData'
        mp_c.order_num = 1
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = 'FBM库存导入'
        mp_c.component = 'fbmStock_import'
        mp_c.order_num = 2
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '盘点数量'
        mp_c.component = 'fbmStock_pandian'
        mp_c.order_num = 3
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '修改状态'
        mp_c.component = 'fbmStock_changeStatus'
        mp_c.order_num = 4
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp = MLUserPermission()
        mp.module_name = '中转仓'
        mp.component = 'tranStock'
        mp.order_num = 5
        mp.is_active = True
        mp.user = User.objects.get(username='admin')
        mp.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = 'FBM发仓'
        mp_c.component = 'tranStock_send'
        mp_c.order_num = 1
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp = MLUserPermission()
        mp.module_name = '销售订单'
        mp.component = 'order'
        mp.order_num = 6
        mp.is_active = True
        mp.user = User.objects.get(username='admin')
        mp.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '销售订单导入'
        mp_c.component = 'order_import'
        mp_c.order_num = 1
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '数据权限: 查看全部店铺订单(没打勾仅查看本人店铺)'
        mp_c.component = 'order_allShopCheck'
        mp_c.order_num = 2
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp = MLUserPermission()
        mp.module_name = '财务管理'
        mp.component = 'finance'
        mp.order_num = 7
        mp.is_active = True
        mp.user = User.objects.get(username='admin')
        mp.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '新增店铺提现'
        mp_c.component = 'finance_shopCreate'
        mp_c.order_num = 1
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '店铺提现确认到账'
        mp_c.component = 'finance_ShopConfirm'
        mp_c.order_num = 2
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '查看资金结汇'
        mp_c.component = 'finance_exchangeList'
        mp_c.order_num = 3
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '新增结汇'
        mp_c.component = 'finance_exchangeCreate'
        mp_c.order_num = 4
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '查看店铺资金'
        mp_c.component = 'finance_shopFinance'
        mp_c.order_num = 5
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '查看全部在途'
        mp_c.component = 'finance_allOnway'
        mp_c.order_num = 6
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp = MLUserPermission()
        mp.module_name = '操作日志'
        mp.component = 'log'
        mp.order_num = 8
        mp.is_active = True
        mp.user = User.objects.get(username='admin')
        mp.save()

        mp = MLUserPermission()
        mp.module_name = '首页'
        mp.component = 'dashboard'
        mp.order_num = 9
        mp.is_active = True
        mp.user = User.objects.get(username='admin')
        mp.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '待办事项-发货运单'
        mp_c.component = 'dashboard_ship'
        mp_c.order_num = 1
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '待办事项-采购管理'
        mp_c.component = 'dashboard_purchase'
        mp_c.order_num = 2
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '销量统计'
        mp_c.component = 'dashboard_saleChart'
        mp_c.order_num = 3
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '收支管理'
        mp_c.component = 'dashboard_shopFinance'
        mp_c.order_num = 4
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp = MLUserPermission()
        mp.module_name = '产品开发'
        mp.component = 'devproduct'
        mp.order_num = 10
        mp.is_active = True
        mp.user = User.objects.get(username='admin')
        mp.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '基本信息-产品导入'
        mp_c.component = 'devproduct_import'
        mp_c.order_num = 1
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '基本信息-产品修改'
        mp_c.component = 'devproduct_edit'
        mp_c.order_num = 2
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '基本信息-产品关联/解除'
        mp_c.component = 'devproduct_cp'
        mp_c.order_num = 3
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '基本信息-产品删除'
        mp_c.component = 'devproduct_delete'
        mp_c.order_num = 4
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '定价-新增定价'
        mp_c.component = 'devproduct_price_add'
        mp_c.order_num = 5
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '定价-操作'
        mp_c.component = 'devproduct_price_op'
        mp_c.order_num = 6
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '查看产品发布渠道'
        mp_c.component = 'devproduct_online_check'
        mp_c.order_num = 7
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '产品发布/取消发布'
        mp_c.component = 'devproduct_online_list'
        mp_c.order_num = 8
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '产品下线'
        mp_c.component = 'devproduct_offline'
        mp_c.order_num = 9
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '产品重新上线'
        mp_c.component = 'devproduct_relist'
        mp_c.order_num = 10
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '备货申请'
        mp_c.component = 'devproduct_buy_req'
        mp_c.order_num = 11
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '备货审批'
        mp_c.component = 'devproduct_buy_check'
        mp_c.order_num = 12
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '备货采购'
        mp_c.component = 'devproduct_buy_make'
        mp_c.order_num = 13
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        mp_c = MLUserPermission()
        mp_c.parent = mp
        mp_c.module_name = '查看数据统计'
        mp_c.component = 'devproduct_check_statistic'
        mp_c.order_num = 14
        mp_c.is_active = True
        mp_c.user = User.objects.get(username='admin')
        mp_c.save()

        return Response({'msg': '创建成功!'}, status=status.HTTP_200_OK)


class MLUserPermissionViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.RetrieveModelMixin,
                              viewsets.GenericViewSet):
    """
    list:
        指定用户美客多操作权限列表
    """
    queryset = MLUserPermission.objects.all()
    serializer_class = MLUserPermissionSerializer  # 序列化

    def get_queryset(self):
        user_id = self.request.GET.get("id")
        # 返回指定用户数据
        user = User.objects.get(id=user_id)
        return MLUserPermission.objects.filter(user=user, parent=None)

    @action(methods=['post'], detail=True, url_path='create_ml_permission')
    def create_ml_permission(self, request, pk):
        user = User.objects.get(id=pk)
        admin = User.objects.get(username='admin')
        queryset = MLUserPermission.objects.filter(user=admin)

        user_count = MLUserPermission.objects.filter(user=user).count()
        admin_count = MLUserPermission.objects.filter(user=admin).count()
        menu_set = MLUserPermission.objects.filter(user=user)
        # 如果菜单数量与admin相同，说明是修改
        if user_count == admin_count:
            menu_set.update(is_active=False)
            p_ids = []
            for i in menu_set:
                for item in queryset:
                    if item.id in request.data:
                        if item.component == i.component:
                            i.is_active = True
                            i.save()
                            if not i.id in p_ids:
                                if i.parent:
                                    p_ids.append(i.parent.id)

            # 如果有子菜单，父菜单设为true
            for i in p_ids:
                m = MLUserPermission.objects.get(id=i)
                m.is_active = True
                m.save()

            return Response({'msg': '修改成功'}, status=status.HTTP_200_OK)

        # 如果是部分菜单新增，则先全部删除，再新增
        if admin_count != user_count and user_count > 0:
            us = MLUserPermission.objects.filter(user=user)
            for i in us:
                if i.parent:
                    i.delete()
            MLUserPermission.objects.filter(user=user).delete()

        # 先创建父菜单
        parent_add_list = []
        for i in queryset:
            if not i.parent:
                parent_add_list.append(
                    MLUserPermission(
                        parent=i.parent,
                        component=i.component,
                        module_name=i.module_name,
                        order_num=i.order_num,
                        user=user,
                        is_active=True if i.id in request.data else False))
        MLUserPermission.objects.bulk_create(parent_add_list)

        # 创建子菜单
        qt = MLUserPermission.objects.filter(user=user)
        children_add_list = []

        for i in qt:
            for item in queryset:
                if item.parent:
                    if item.parent.component == i.component:
                        children_add_list.append(
                            MLUserPermission(parent=i,
                                             component=item.component,
                                             module_name=item.module_name,
                                             order_num=item.order_num,
                                             user=user,
                                             is_active=True if item.id
                                             in request.data else False))
                        i.is_active = True
                        i.save()
        MLUserPermission.objects.bulk_create(children_add_list)

        return Response({'msg': '创建成功'}, status=status.HTTP_200_OK)


class MLPermissionViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                          mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                          mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        前端指定用户美客多操作权限列表
    """
    queryset = MLUserPermission.objects.all()
    serializer_class = MLPermissionSerializer  # 序列化

    def get_queryset(self):
        # 返回当前用户数据
        return MLUserPermission.objects.filter(user=self.request.user)


class UserViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                  mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        user信息
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer  # 序列化

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)  # 过滤,搜索
    filter_fields = ('is_staff', 'is_active', 'is_superuser', 'last_name'
                     )  # 配置过滤字段
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
            return Response({
                'msg': '手机号已存在!',
                'success': False
            },
                            status=status.HTTP_202_ACCEPTED)

        user = User()
        user.username = username
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.is_superuser = is_superuser
        user.save()

        return Response(
            {
                'msg': '创建成功!',
                'success': True,
                'id': user.id,
                'name': user.first_name
            },
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


class SysRefillViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                       mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                       mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        补货推荐设置列表
    """
    queryset = SysRefill.objects.all()
    serializer_class = SysRefillSerializer  # 序列化
