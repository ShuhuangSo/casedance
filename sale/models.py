from django.db import models

# Create your models here.
from product.models import ProductExtraInfo
from setting.models import Tag


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
