from django.db import models
from django.contrib.auth import get_user_model

from store.models import Store
from product.models import Supplier

from product.models import Product

# Create your models here.
User = get_user_model()


class PurchaseOrder(models.Model):
    """
    采购单
    """
    P_STATUS = (
        ('UNPAID', '未结算'),
        ('PART_PAID', '部分结算'),
        ('FULL_PAID', '全部结算'),
    )
    O_STATUS = (
        ('CANCEL', '作废'),
        ('WAIT_CONFIRM', '待确认'),
        ('IN_PRODUCTION', '生产中'),
        ('SENT', '已发货'),
        ('PART_REC', '部分收货'),
        ('FINISHED', '已完成'),
        ('EXCEPTION', '异常'),
    )

    p_number = models.CharField(max_length=20, verbose_name='采购单号', help_text='采购单号')
    store = models.ForeignKey(Store, null=True, related_name='store_purchase_order', on_delete=models.DO_NOTHING,
                              verbose_name='收货仓库/店铺', help_text='收货仓库/店铺')
    supplier = models.ForeignKey(Supplier, null=True, related_name='supplier_purchase_order',
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='供应商', help_text='供应商')
    user = models.ForeignKey(User, null=True, related_name='user_purchase_order', on_delete=models.DO_NOTHING,
                             verbose_name='操作人',
                             help_text='操作人')
    logistic = models.CharField(null=True, blank=True, max_length=20, verbose_name='发货物流公司', help_text='发货物流公司')
    tracking_number = models.CharField(null=True, blank=True, max_length=30, verbose_name='快递单号', help_text='快递单号')
    postage = models.FloatField(default=0.0, verbose_name='采购运费', help_text='采购运费')
    total_cost = models.FloatField(default=0.0, verbose_name='采购单总金额', help_text='采购单总金额')
    total_paid = models.FloatField(default=0.0, verbose_name='已结算总金额', help_text='已结算总金额')
    paid_status = models.CharField(max_length=20, choices=P_STATUS, default='UNPAID', verbose_name='结算状态',
                                   help_text='结算状态')
    order_status = models.CharField(max_length=20, choices=O_STATUS, default='WAIT_CONFIRM', verbose_name='采购单状态',
                                    help_text='采购单状态')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='状态', help_text='状态')

    class Meta:
        verbose_name = '采购单'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.p_number


class PurchaseDetail(models.Model):
    """
    采购商品明细
    """

    purchase_order = models.ForeignKey(PurchaseOrder, related_name='purchase_detail', on_delete=models.CASCADE,
                                       verbose_name='所属采购单',
                                       help_text='所属采购单')
    product = models.ForeignKey(Product, related_name='product_purchase_detail', on_delete=models.DO_NOTHING,
                                verbose_name='产品',
                                help_text='产品')
    qty = models.IntegerField(default=0, verbose_name='采购数量', help_text='采购数量')
    unit_cost = models.FloatField(default=0.0, verbose_name='采购单价', help_text='采购单价')
    received_qty = models.IntegerField(default=0, verbose_name='收货入库数量', help_text='收货入库数量')
    paid_qty = models.IntegerField(default=0, verbose_name='已结算数量', help_text='已结算数量')
    is_paid = models.BooleanField(default=False, verbose_name='是否已结算', help_text='是否已结算')
    short_note = models.CharField(null=True, blank=True, max_length=100, default='', verbose_name='简短备注', help_text='简短备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    stock_before = models.IntegerField(default=0, verbose_name='采购前库存', help_text='采购前库存')

    class Meta:
        verbose_name = '采购商品明细'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return str(self.qty)
