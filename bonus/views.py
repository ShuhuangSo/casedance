from rest_framework import mixins, status
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response

from bonus.models import AccountSales, AccountBonus, Accounts, MonthList, ExchangeRate, BasicInfo
from bonus.serializers import AccountSalesSerializer, AccountBonusSerializer, AccountsSerializer, MonthListSerializer, \
    ExchangeRateSerializer, BasicInfoSerializer


class DefaultPagination(PageNumberPagination):
    """
    分页设置
    """
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100


class AccountSalesViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """
    list:
        账号销售,分页,过滤,搜索,排序
    create:
        账号销售新增
    retrieve:
        账号销售详情页
    update:
        账号销售修改
    destroy:
        账号销售删除
    """
    queryset = AccountSales.objects.all()
    serializer_class = AccountSalesSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)  # 过滤,搜索,排序
    filter_fields = ('platform', 'platform_base', 'account_name', 'manager', 'month')  # 配置过滤字段
    search_fields = ('account_name',)  # 配置搜索字段


class AccountBonusViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """
    list:
        提成表,分页,过滤,搜索,排序
    create:
        提成表新增
    retrieve:
        提成表详情页
    update:
        提成表修改
    destroy:
        提成表删除
    """
    queryset = AccountBonus.objects.all()
    serializer_class = AccountBonusSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)  # 过滤,搜索,排序
    filter_fields = ('platform', 'platform_base', 'account_name', 'manager', 'month')  # 配置过滤字段
    search_fields = ('account_name',)  # 配置搜索字段

    # 生成提成表
    @action(methods=['post'], detail=False, url_path='create_bonus')
    def create_bonus(self, request):
        month = request.data['month']
        account_sales = AccountSales.objects.filter(month=month)
        for i in account_sales:
            account_bonus = AccountBonus.objects.filter(month=month, account_name=i.account_name, platform=i.platform).first()
            if account_bonus:
                account_bonus.platform_base = i.platform_base
                account_bonus.manager = i.manager
                account_bonus.ori_currency = i.ori_currency
                account_bonus.currency_rate = i.currency_rate
                account_bonus.sale_amount = i.sale_amount
                account_bonus.sale_income = i.sale_income
                account_bonus.receipts = i.receipts
                account_bonus.refund = i.refund
                account_bonus.FES = i.FES
                account_bonus.platform_fees = i.platform_fees
                account_bonus.platform_fees_rmb = i.platform_fees_rmb
                account_bonus.product_cost = i.product_cost
                account_bonus.shipping_cost = i.shipping_cost
                account_bonus.profit = i.profit
                account_bonus.profit_margin = i.profit_margin
                account_bonus.month_profit = i.month_profit
                account_bonus.orders = i.orders
                account_bonus.CUP = i.CUP
                account_bonus.ad_fees = i.ad_fees
                account_bonus.ad_fees_rmb = i.ad_fees_rmb
                account_bonus.ad_percent = i.ad_percent
                account_bonus.cp_cgf_fees = i.cp_cgf_fees
                account_bonus.cp_first_ship = i.cp_first_ship
                account_bonus.bonus_rate = i.manager.bonus_rate
                account_bonus.bonus = i.profit * i.manager.bonus_rate
                account_bonus.save()
            else:
                account_bonus = AccountBonus()
                account_bonus.platform = i.platform
                account_bonus.platform_base = i.platform_base
                account_bonus.account_name = i.account_name
                account_bonus.manager = i.manager
                account_bonus.month = i.month
                account_bonus.ori_currency = i.ori_currency
                account_bonus.currency_rate = i.currency_rate
                account_bonus.sale_amount = i.sale_amount
                account_bonus.sale_income = i.sale_income
                account_bonus.receipts = i.receipts
                account_bonus.refund = i.refund
                account_bonus.FES = i.FES
                account_bonus.platform_fees = i.platform_fees
                account_bonus.platform_fees_rmb = i.platform_fees_rmb
                account_bonus.product_cost = i.product_cost
                account_bonus.shipping_cost = i.shipping_cost
                account_bonus.profit = i.profit
                account_bonus.profit_margin = i.profit_margin
                account_bonus.month_profit = i.month_profit
                account_bonus.orders = i.orders
                account_bonus.CUP = i.CUP
                account_bonus.ad_fees = i.ad_fees
                account_bonus.ad_fees_rmb = i.ad_fees_rmb
                account_bonus.ad_percent = i.ad_percent
                account_bonus.cp_cgf_fees = i.cp_cgf_fees
                account_bonus.cp_first_ship = i.cp_first_ship
                account_bonus.bonus_rate = i.manager.bonus_rate
                account_bonus.bonus = i.profit * i.manager.bonus_rate
                account_bonus.save()
        return Response({'msg': '操作成功'}, status=status.HTTP_200_OK)


class AccountsViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    """
    list:
        帐号,分页,过滤,搜索,排序
    create:
        帐号新增
    retrieve:
        帐号详情页
    update:
        帐号修改
    destroy:
        帐号删除
    """
    queryset = Accounts.objects.all()
    serializer_class = AccountsSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)  # 过滤,搜索,排序
    filter_fields = ('type',)  # 配置过滤字段
    search_fields = ('name',)  # 配置搜索字段


class MonthListViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    """
    list:
        统计月份,分页,过滤,搜索,排序
    create:
        统计月份新增
    retrieve:
        统计月份详情页
    update:
        统计月份修改
    destroy:
        统计月份删除
    """
    queryset = MonthList.objects.all()
    serializer_class = MonthListSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)  # 过滤,搜索,排序
    filter_fields = ('status',)  # 配置过滤字段
    search_fields = ('month',)  # 配置搜索字段

    # 生成当月月份
    @action(methods=['get'], detail=False, url_path='create_month')
    def create_month(self, request):
        from . import tasks
        tasks.create_month()
        return Response({'msg': '操作成功'}, status=status.HTTP_200_OK)


class ExchangeRateViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """
    list:
        汇率,分页,过滤,搜索,排序
    create:
        汇率新增
    retrieve:
        汇率详情页
    update:
        汇率修改
    destroy:
        汇率删除
    """
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)  # 过滤,搜索,排序
    filter_fields = ('currency', 'month')  # 配置过滤字段
    search_fields = ('month',)  # 配置搜索字段


class BasicInfoViewSet(mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    """
    list:
        基础信息设置,分页,过滤,搜索,排序
    create:
        基础信息设置新增
    retrieve:
        基础信息设置详情页
    update:
        基础信息设置修改
    destroy:
        基础信息设置删除
    """
    queryset = BasicInfo.objects.all()
    serializer_class = BasicInfoSerializer  # 序列化
    pagination_class = DefaultPagination  # 分页

    filter_backends = (DjangoFilterBackend, filters.SearchFilter)  # 过滤,搜索,排序
    filter_fields = ('type', 'platform')  # 配置过滤字段
    search_fields = ('name',)  # 配置搜索字段
