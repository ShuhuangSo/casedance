from django.db import models


class ExchangeRate(models.Model):
    """
    汇率
    """
    currency = models.CharField(null=True,
                                blank=True,
                                max_length=10,
                                verbose_name='币种',
                                help_text='币种')
    rate = models.FloatField(null=True,
                             blank=True,
                             verbose_name='汇率值',
                             help_text='汇率值')
    month = models.CharField(null=True,
                             blank=True,
                             max_length=10,
                             verbose_name='月份',
                             help_text='月份')

    class Meta:
        verbose_name = '汇率'
        verbose_name_plural = verbose_name
        ordering = ['-month']

    def __str__(self):
        return self.currency


class BasicInfo(models.Model):
    """
    基础信息设置
    """
    INFO = (
        ('PLATFORM', '平台'),
        ('BASE', '平台站点'),
    )
    type = models.CharField(max_length=10,
                            choices=INFO,
                            default='PLATFORM',
                            verbose_name='信息类型',
                            help_text='信息类型')
    platform = models.CharField(null=True,
                                blank=True,
                                max_length=30,
                                verbose_name='所属平台',
                                help_text='所属平台')
    name = models.CharField(null=True,
                            blank=True,
                            max_length=30,
                            verbose_name='信息名称',
                            help_text='信息名称')

    class Meta:
        verbose_name = '基础信息设置'
        verbose_name_plural = verbose_name
        ordering = ['-name']

    def __str__(self):
        return self.name


class MonthList(models.Model):
    """
    统计月份
    """
    month = models.CharField(null=True,
                             blank=True,
                             max_length=10,
                             verbose_name='月份',
                             help_text='月份')
    status = models.BooleanField(default=False,
                                 verbose_name='状态',
                                 help_text='状态')

    class Meta:
        verbose_name = '统计月份'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.month


class Manager(models.Model):
    """
    运营负责人
    """

    name = models.CharField(null=True,
                            blank=True,
                            max_length=30,
                            verbose_name='负责人名称',
                            help_text='负责人名称')
    is_leader = models.BooleanField(default=False,
                                    verbose_name='是否组长',
                                    help_text='是否组长')
    bonus_rate = models.FloatField(null=True,
                                   blank=True,
                                   verbose_name='提成点数',
                                   help_text='提成点数')
    team = models.IntegerField(default=1,
                               null=True,
                               blank=True,
                               verbose_name='所属小组',
                               help_text='所属小组')
    is_active = models.BooleanField(default=True,
                                    verbose_name='是否启用',
                                    help_text='是否启用')

    class Meta:
        verbose_name = '运营负责人'
        verbose_name_plural = verbose_name
        ordering = ['-name']

    def __str__(self):
        return self.name


class Accounts(models.Model):
    """
    帐号
    """
    type = models.CharField(null=True,
                            blank=True,
                            max_length=30,
                            verbose_name='平台',
                            help_text='平台')
    ac_type = models.CharField(null=True,
                               blank=True,
                               default='CHINA',
                               max_length=10,
                               verbose_name='账号类型',
                               help_text='账号类型')
    site = models.CharField(null=True,
                            blank=True,
                            max_length=30,
                            verbose_name='站点',
                            help_text='站点')
    name = models.CharField(null=True,
                            blank=True,
                            max_length=30,
                            verbose_name='帐号名称',
                            help_text='帐号名称')
    manager = models.ForeignKey(Manager,
                                null=True,
                                related_name='manager_accounts',
                                on_delete=models.DO_NOTHING,
                                verbose_name='账号负责人',
                                help_text='账号负责人')
    note = models.CharField(null=True,
                            blank=True,
                            max_length=100,
                            verbose_name='备注',
                            help_text='备注')
    is_active = models.BooleanField(default=True,
                                    verbose_name='是否启用',
                                    help_text='是否启用')

    class Meta:
        verbose_name = '帐号'
        verbose_name_plural = verbose_name
        ordering = ['-name']

    def __str__(self):
        return self.name


class AccountSales(models.Model):
    """
    账号销售报表
    """

    platform = models.CharField(null=True,
                                blank=True,
                                max_length=30,
                                verbose_name='平台',
                                help_text='平台')
    platform_base = models.CharField(null=True,
                                     blank=True,
                                     max_length=30,
                                     verbose_name='平台站点',
                                     help_text='平台站点')
    account_name = models.CharField(null=True,
                                    blank=True,
                                    max_length=30,
                                    verbose_name='账号名称',
                                    help_text='账号名称')
    manager = models.ForeignKey(Manager,
                                null=True,
                                related_name='manager_sales',
                                on_delete=models.DO_NOTHING,
                                verbose_name='账号负责人',
                                help_text='账号负责人')
    month = models.CharField(null=True,
                             blank=True,
                             max_length=10,
                             verbose_name='月份',
                             help_text='月份')
    ori_currency = models.CharField(null=True,
                                    blank=True,
                                    max_length=10,
                                    verbose_name='原始币种',
                                    help_text='原始币种')
    currency_rate = models.FloatField(null=True,
                                      blank=True,
                                      verbose_name='汇率值',
                                      help_text='汇率值')
    sale_amount = models.FloatField(null=True,
                                    blank=True,
                                    verbose_name='销售额 (原始货币)',
                                    help_text='销售额 (原始货币)')
    sale_income = models.FloatField(null=True,
                                    blank=True,
                                    verbose_name='销售收入(原始货币)',
                                    help_text='销售收入(原始货币)')
    receipts = models.FloatField(null=True,
                                 blank=True,
                                 verbose_name='净收款 (原始货币)',
                                 help_text='净收款 (原始货币)')
    refund = models.FloatField(null=True,
                               blank=True,
                               verbose_name='退款(原始货币)',
                               help_text='退款(原始货币)')
    FES = models.FloatField(null=True,
                            blank=True,
                            verbose_name='结汇收入(人民币)',
                            help_text='结汇收入(人民币)')
    platform_fees = models.FloatField(null=True,
                                      blank=True,
                                      verbose_name='平台费用 (原始货币)',
                                      help_text='平台费用 (原始货币)')
    platform_fees_rmb = models.FloatField(null=True,
                                          blank=True,
                                          verbose_name='平台费用 (rmb)',
                                          help_text='平台费用 (rmb)')
    product_cost = models.FloatField(null=True,
                                     blank=True,
                                     verbose_name='产品成本 (人民币)',
                                     help_text='产品成本 (人民币)')
    shipping_cost = models.FloatField(null=True,
                                      blank=True,
                                      verbose_name='物流成本(人民币)',
                                      help_text='物流成本(人民币)')
    profit = models.FloatField(null=True,
                               blank=True,
                               verbose_name='毛利润(人民币)',
                               help_text='毛利润(人民币)')
    profit_margin = models.FloatField(null=True,
                                      blank=True,
                                      verbose_name='毛利率',
                                      help_text='毛利率')
    month_profit = models.FloatField(null=True,
                                     blank=True,
                                     verbose_name='当月毛利润(人民币)',
                                     help_text='当月毛利润(人民币)')
    orders = models.IntegerField(default=0,
                                 null=True,
                                 blank=True,
                                 verbose_name='订单数',
                                 help_text='订单数')
    CUP = models.FloatField(null=True,
                            blank=True,
                            verbose_name='平均客单价',
                            help_text='平均客单价')
    ad_fees = models.FloatField(null=True,
                                blank=True,
                                verbose_name='广告费(原始货币)',
                                help_text='广告费(原始货币)')
    ad_fees_rmb = models.FloatField(null=True,
                                    blank=True,
                                    verbose_name='广告费(rmb)',
                                    help_text='广告费(rmb)')
    ad_percent = models.FloatField(null=True,
                                   blank=True,
                                   verbose_name='广告费占比',
                                   help_text='广告费占比')
    cp_cgf_fees = models.FloatField(null=True,
                                    blank=True,
                                    verbose_name='CGF费用',
                                    help_text='CGF费用')
    cp_first_ship = models.FloatField(null=True,
                                      blank=True,
                                      verbose_name='CGF发仓运费',
                                      help_text='CGF发仓运费')

    class Meta:
        verbose_name = '账号销售报表'
        verbose_name_plural = verbose_name
        ordering = ['-month']

    def __str__(self):
        return self.account_name


class AccountBonus(models.Model):
    """
    提成表
    """

    platform = models.CharField(null=True,
                                blank=True,
                                max_length=30,
                                verbose_name='平台',
                                help_text='平台')
    platform_base = models.CharField(null=True,
                                     blank=True,
                                     max_length=30,
                                     verbose_name='平台站点',
                                     help_text='平台站点')
    account_name = models.CharField(null=True,
                                    blank=True,
                                    max_length=30,
                                    verbose_name='账号名称',
                                    help_text='账号名称')
    manager = models.ForeignKey(Manager,
                                null=True,
                                related_name='manager_bonus',
                                on_delete=models.DO_NOTHING,
                                verbose_name='账号负责人',
                                help_text='账号负责人')
    month = models.CharField(null=True,
                             blank=True,
                             max_length=10,
                             verbose_name='月份',
                             help_text='月份')
    ori_currency = models.CharField(null=True,
                                    blank=True,
                                    max_length=10,
                                    verbose_name='原始币种',
                                    help_text='原始币种')
    currency_rate = models.FloatField(null=True,
                                      blank=True,
                                      verbose_name='汇率值',
                                      help_text='汇率值')
    sale_amount = models.FloatField(null=True,
                                    blank=True,
                                    verbose_name='销售额 (原始货币)',
                                    help_text='销售额 (原始货币)')
    sale_income = models.FloatField(null=True,
                                    blank=True,
                                    verbose_name='销售收入(原始货币)',
                                    help_text='销售收入(原始货币)')
    receipts = models.FloatField(null=True,
                                 blank=True,
                                 verbose_name='净收款 (原始货币)',
                                 help_text='净收款 (原始货币)')
    refund = models.FloatField(null=True,
                               blank=True,
                               verbose_name='退款(原始货币)',
                               help_text='退款(原始货币)')
    FES = models.FloatField(null=True,
                            blank=True,
                            verbose_name='结汇收入(人民币)',
                            help_text='结汇收入(人民币)')
    platform_fees = models.FloatField(null=True,
                                      blank=True,
                                      verbose_name='平台费用 (原始货币)',
                                      help_text='平台费用 (原始货币)')
    platform_fees_rmb = models.FloatField(null=True,
                                          blank=True,
                                          verbose_name='平台费用 (rmb)',
                                          help_text='平台费用 (rmb)')
    product_cost = models.FloatField(null=True,
                                     blank=True,
                                     verbose_name='产品成本 (人民币)',
                                     help_text='产品成本 (人民币)')
    shipping_cost = models.FloatField(null=True,
                                      blank=True,
                                      verbose_name='物流成本(人民币)',
                                      help_text='物流成本(人民币)')
    profit = models.FloatField(null=True,
                               blank=True,
                               verbose_name='毛利润(人民币)',
                               help_text='毛利润(人民币)')
    profit_margin = models.FloatField(null=True,
                                      blank=True,
                                      verbose_name='毛利率',
                                      help_text='毛利率')
    month_profit = models.FloatField(null=True,
                                     blank=True,
                                     verbose_name='当月毛利润(人民币)',
                                     help_text='当月毛利润(人民币)')
    orders = models.IntegerField(default=0,
                                 null=True,
                                 blank=True,
                                 verbose_name='订单数',
                                 help_text='订单数')
    CUP = models.FloatField(null=True,
                            blank=True,
                            verbose_name='平均客单价',
                            help_text='平均客单价')
    ad_fees = models.FloatField(null=True,
                                blank=True,
                                verbose_name='广告费(原始货币)',
                                help_text='广告费(原始货币)')
    ad_fees_rmb = models.FloatField(null=True,
                                    blank=True,
                                    verbose_name='广告费(rmb)',
                                    help_text='广告费(rmb)')
    ad_percent = models.FloatField(null=True,
                                   blank=True,
                                   verbose_name='广告费占比',
                                   help_text='广告费占比')
    cp_cgf_fees = models.FloatField(null=True,
                                    blank=True,
                                    verbose_name='CGF费用',
                                    help_text='CGF费用')
    cp_first_ship = models.FloatField(null=True,
                                      blank=True,
                                      verbose_name='CGF发仓运费',
                                      help_text='CGF发仓运费')
    bonus_rate = models.FloatField(null=True,
                                   blank=True,
                                   verbose_name='提成点数',
                                   help_text='提成点数')
    bonus = models.FloatField(null=True,
                              blank=True,
                              verbose_name='提成金额',
                              help_text='提成金额')
    is_calc = models.BooleanField(default=False,
                                  verbose_name='是否记入提成',
                                  help_text='是否记入提成')

    class Meta:
        verbose_name = '提成表'
        verbose_name_plural = verbose_name
        ordering = ['-month']

    def __str__(self):
        return self.account_name
