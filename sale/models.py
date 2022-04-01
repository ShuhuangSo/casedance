from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
from product.models import ProductExtraInfo, Product
from setting.models import Tag
from store.models import Store

User = get_user_model()


class Customer(models.Model):
    """
    客户
    """
    WAY = (
        ('PAY_NOW', '现结'),
        ('CONTRACT', '约定付款'),
    )

    company_name = models.CharField(max_length=80, unique=True, verbose_name='公司名称', help_text='公司名称')
    customer_code = models.CharField(max_length=20, unique=True, verbose_name='客户编码', help_text='客户编码')
    pay_way = models.CharField(max_length=10, choices=WAY, default='FACTORY', verbose_name='结算类型',
                               help_text='结算类型')
    address = models.CharField(null=True, blank=True, max_length=200, verbose_name='地址', help_text='地址')
    contact_name = models.CharField(null=True, blank=True, max_length=20, verbose_name='联系人', help_text='联系人')
    phone = models.CharField(null=True, blank=True, max_length=15, verbose_name='电话', help_text='电话')
    qq = models.CharField(null=True, blank=True, max_length=15, verbose_name='QQ', help_text='QQ')
    wechat = models.CharField(null=True, blank=True, max_length=15, verbose_name='微信', help_text='微信')
    email = models.CharField(null=True, blank=True, max_length=50, verbose_name='邮箱', help_text='邮箱')
    level = models.IntegerField(default=1, verbose_name='客户评级', help_text='客户评级')
    is_active = models.BooleanField(default=True, verbose_name='状态', help_text='状态')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '客户'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.company_name


class CustomerDiscount(models.Model):
    """
    客户专属优惠
    """

    customer = models.ForeignKey(Customer, related_name='customer_discount', on_delete=models.CASCADE,
                                 verbose_name='客户', help_text='客户')
    p_series = models.ForeignKey(ProductExtraInfo, related_name='p_series_discount', on_delete=models.CASCADE,
                                 verbose_name='产品系列', help_text='产品系列')
    discount_type = models.IntegerField(default=1, verbose_name='折扣类型', help_text='折扣类型')  # 1：金额数， 0：百分比
    discount_money = models.FloatField(default=0.0, verbose_name='优惠额度', help_text='优惠额度')
    discount_percent = models.FloatField(default=0.0, verbose_name='优惠比例', help_text='优惠比例')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '客户专属优惠'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return str(self.discount_type)


class CustomerTag(models.Model):
    """
    客户标签
    """

    customer = models.ForeignKey(Customer, related_name='customer_tag', on_delete=models.CASCADE,
                                 verbose_name='客户',
                                 help_text='客户')
    tag = models.ForeignKey(Tag, related_name='tag_customer_tag', on_delete=models.CASCADE, verbose_name='标签',
                            help_text='标签')

    class Meta:
        verbose_name = '客户标签'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return str(self.id)


class Order(models.Model):
    """
    销售订单
    """
    O_TYPE = (
        ('PICKUP', '门店自提'),
        ('EXPRESS', '快递'),
        ('SELLER_SEND', '卖家送货'),
    )
    WAY = (
        ('PAY_NOW', '现结'),
        ('CONTRACT', '约定付款'),
    )
    P_STATUS = (
        ('UNPAID', '未结算'),
        ('PART_PAID', '部分结算'),
        ('FULL_PAID', '全部结算'),
    )
    O_STATUS = (
        ('CANCEL', '作废'),
        ('PRE_SUMMIT', '待处理'),
        ('PREPARING', '备货中'),
        ('READY', '已备货'),
        ('SENDING', '送货中'),
        ('PART_SENT', '部分发货'),
        ('FINISHED', '已完成'),
        ('EXCEPTION', '异常'),
    )

    order_number = models.CharField(max_length=30, verbose_name='销售单号', help_text='销售单号')
    store = models.ForeignKey(Store, null=True, related_name='store_order', on_delete=models.DO_NOTHING,
                              verbose_name='收货仓库/店铺', help_text='收货仓库/店铺')
    customer = models.ForeignKey(Customer, null=True, related_name='customer_order',
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='客户', help_text='客户')
    user = models.ForeignKey(User, null=True, related_name='user_order', on_delete=models.DO_NOTHING,
                             verbose_name='操作人',
                             help_text='操作人')
    order_type = models.CharField(max_length=20, choices=O_TYPE, default='PICKUP', verbose_name='订单类型',
                                  help_text='订单类型')
    order_status = models.CharField(max_length=20, choices=O_STATUS, default='PRE_SUMMIT', verbose_name='订单状态',
                                    help_text='订单状态')
    pay_way = models.CharField(max_length=20, choices=WAY, default='PAY_NOW', verbose_name='结算类型',
                               help_text='结算类型')
    paid_status = models.CharField(max_length=20, choices=P_STATUS, default='UNPAID', verbose_name='结算状态',
                                   help_text='结算状态')
    address = models.CharField(null=True, blank=True, max_length=200, verbose_name='地址', help_text='地址')
    contact_name = models.CharField(null=True, blank=True, max_length=20, verbose_name='联系人', help_text='联系人')
    phone = models.CharField(null=True, blank=True, max_length=15, verbose_name='电话', help_text='电话')
    logistic = models.CharField(null=True, blank=True, max_length=20, verbose_name='发货物流公司', help_text='发货物流公司')
    tracking_number = models.CharField(null=True, blank=True, max_length=30, verbose_name='快递单号', help_text='快递单号')
    postage = models.FloatField(default=0.0, verbose_name='采购运费', help_text='采购运费')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='状态', help_text='状态')

    class Meta:
        verbose_name = '销售订单'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.order_number


class OrderDetail(models.Model):
    """
    销售单明细
    """

    order = models.ForeignKey(Order, related_name='order_detail', on_delete=models.CASCADE,
                              verbose_name='所属销售单',
                              help_text='所属销售单')
    product = models.ForeignKey(Product, related_name='product_order_detail', on_delete=models.DO_NOTHING,
                                verbose_name='产品',
                                help_text='产品')
    qty = models.IntegerField(default=0, verbose_name='销售数量', help_text='销售数量')
    unit_price = models.FloatField(default=0.0, verbose_name='销售单价', help_text='销售单价')
    sold_price = models.FloatField(default=0.0, verbose_name='成交价', help_text='成交价')
    sent_qty = models.IntegerField(default=0, verbose_name='发货数量', help_text='发货数量')
    paid_qty = models.IntegerField(default=0, verbose_name='已结算数量', help_text='已结算数量')
    is_paid = models.BooleanField(default=False, verbose_name='是否已结算', help_text='是否已结算')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '销售单明细'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return str(self.qty)


class OrderTag(models.Model):
    """
    销售单标签
    """

    order = models.ForeignKey(Order, related_name='order_tag', on_delete=models.CASCADE,
                              verbose_name='销售单',
                              help_text='销售单')
    tag = models.ForeignKey(Tag, related_name='tag_order_tag', on_delete=models.CASCADE, verbose_name='标签',
                            help_text='标签')

    class Meta:
        verbose_name = '销售单标签'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return str(self.id)
