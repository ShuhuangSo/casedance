from django.db import models
from django.contrib.auth import get_user_model

from product.models import Product

# Create your models here.
User = get_user_model()


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


class StockInOut(models.Model):
    """
    手工出入库/调拨
    """
    INOUT_TYPE = (
        ('IN', '入库'),
        ('OUT', '出库'),
        ('MOVE', '调拨'),
        ('TAKING', '盘点'),
    )
    R_IN = (
        ('RETURN', '客户退货'),
        ('OTHERS', '其它原因'),
    )
    R_OUT = (
        ('GIFT', '非销售出库'),
        ('LOST', '丢失'),
        ('OTHERS', '其它原因'),
    )
    R_MOVE = (
        ('SUPPORT', '库存支援'),
        ('OTHERS', '其它原因'),
    )

    batch_number = models.CharField(max_length=30, verbose_name='批次号', help_text='批次号')
    origin_store = models.ForeignKey(Store, null=True, related_name='store_inout_or', on_delete=models.CASCADE,
                                     verbose_name='源仓库/店铺',
                                     help_text='源仓库/店铺')
    target_store = models.ForeignKey(Store, null=True, related_name='store_inout_ta', on_delete=models.CASCADE,
                                     verbose_name='目标仓库/店铺',
                                     help_text='目标仓库/店铺')
    user = models.ForeignKey(User, null=True, related_name='user_store_inout', on_delete=models.CASCADE,
                             verbose_name='操作人',
                             help_text='操作人')
    type = models.CharField(max_length=10, choices=INOUT_TYPE, default='IN', verbose_name='类型',
                            help_text='类型')
    reason_in = models.CharField(max_length=10, choices=R_IN, default='RETURN', verbose_name='入库原因',
                                 help_text='入库原因')
    reason_out = models.CharField(max_length=10, choices=R_OUT, default='LOST', verbose_name='出库原因',
                                  help_text='出库原因')
    reason_move = models.CharField(max_length=10, choices=R_MOVE, default='SUPPORT', verbose_name='调拨原因',
                                   help_text='调拨原因')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='状态', help_text='状态')

    class Meta:
        verbose_name = '手工出入库/调拨'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.batch_number


class StockInOutDetail(models.Model):
    """
    出入库产品明细
    """

    stock_in_out = models.ForeignKey(StockInOut, related_name='inout_detail', on_delete=models.CASCADE,
                                     verbose_name='所属出入库单',
                                     help_text='所属出入库单')
    product = models.ForeignKey(Product, related_name='product_inout_detail', on_delete=models.DO_NOTHING,
                                verbose_name='产品',
                                help_text='产品')
    qty = models.IntegerField(default=0, verbose_name='出入数量', help_text='出入数量')
    stock_before = models.IntegerField(default=0, verbose_name='变动前库存', help_text='变动前库存')

    class Meta:
        verbose_name = '出入库产品明细'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return str(self.qty)


class StockLog(models.Model):
    """
    库存出入日志
    """
    O_TYPE = (
        ('M_IN', '手工入库'),
        ('M_OUT', '手工出库'),
        ('B_IN', '采购入库'),
        ('S_OUT', '销售出库'),
        ('LOCK', '锁仓'),
        ('UNLOCK', '解锁'),
        ('TAKING', '库存盘点'),
    )

    op_type = models.CharField(max_length=10, choices=O_TYPE, default='S_OUT', verbose_name='日志类型',
                               help_text='日志类型')
    op_origin_id = models.IntegerField(null=True, blank=True, verbose_name='操作单id', help_text='操作单id')
    qty = models.IntegerField(null=True, blank=True, default=0, verbose_name='数量', help_text='数量')
    user = models.ForeignKey(User, related_name='user_stock_log', on_delete=models.DO_NOTHING, null=True,
                             verbose_name='user', help_text='user')
    store = models.ForeignKey(Store, related_name='store_stock_log', on_delete=models.DO_NOTHING, null=True,
                              verbose_name='店铺', help_text='店铺')
    product = models.ForeignKey(Product, related_name='product_stock_log', on_delete=models.DO_NOTHING, null=True,
                                verbose_name='产品', help_text='产品')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间', help_text='操作时间')

    class Meta:
        verbose_name = '库存出入日志'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.op_type
