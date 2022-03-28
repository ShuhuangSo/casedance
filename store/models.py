from django.db import models

# Create your models here.
from product.models import Product


class Store(models.Model):
    """
    仓库、销售门店
    """
    S_TYPE = (
        ('WAREHOUSE', '仓库'),
        ('STORE', '门店'),
    )

    store_name = models.CharField(max_length=80, verbose_name='店铺名称', help_text='店铺名称')
    type = models.CharField(max_length=10, choices=S_TYPE, default='STORE', verbose_name='店铺类型',
                            help_text='店铺类型')
    address = models.CharField(null=True, blank=True, max_length=200, verbose_name='地址', help_text='地址')
    contact_name = models.CharField(null=True, blank=True, max_length=20, verbose_name='联系人', help_text='联系人')
    phone = models.CharField(null=True, blank=True, max_length=15, verbose_name='电话', help_text='电话')
    qq = models.CharField(null=True, blank=True, max_length=15, verbose_name='QQ', help_text='QQ')
    wechat = models.CharField(null=True, blank=True, max_length=15, verbose_name='微信', help_text='微信')
    website = models.CharField(null=True, blank=True, max_length=200, verbose_name='网址', help_text='网址')
    is_active = models.BooleanField(default=True, verbose_name='状态', help_text='状态')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '销售门店'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.store_name


class Stock(models.Model):
    """
    产品库存
    """

    qty = models.IntegerField(default=0, verbose_name='库存数量', help_text='库存数量')
    lock_qty = models.IntegerField(default=0, verbose_name='锁定库存量', help_text='锁定库存量')
    product = models.ForeignKey(Product, related_name='product_stock', on_delete=models.CASCADE, verbose_name='产品',
                                help_text='产品')
    store = models.ForeignKey(Store, related_name='store_stock', on_delete=models.CASCADE, verbose_name='门店',
                              help_text='门店')
    avg_sales = models.FloatField(default=0.0, verbose_name='日均销量', help_text='日均销量')
    recent_7d_sales = models.IntegerField(default=0, verbose_name='最近7天销量', help_text='最近7天销量')
    recent_30d_sales = models.IntegerField(default=0, verbose_name='最近30天销量', help_text='最近30天销量')
    last_sale_time = models.DateTimeField(null=True, blank=True, verbose_name='最后一次销售时间', help_text='最后一次销售时间')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='状态', help_text='状态')

    class Meta:
        verbose_name = '产品库存'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return str(self.qty)
