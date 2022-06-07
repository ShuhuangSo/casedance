from django.db import models

# Create your models here.
from product.models import Product
from sale.models import Customer


class SalesReport(models.Model):
    """
    销量统计
    """
    qty = models.IntegerField(default=0, verbose_name='总销量', help_text='总销量')
    amount = models.FloatField(default=0.0, verbose_name='销售金额', help_text='销售金额')
    series = models.CharField(null=True, blank=True, max_length=30, verbose_name='产品系列', help_text='产品系列')
    sale_date = models.DateField(null=True, blank=True, verbose_name='销售日期', help_text='销售日期')

    class Meta:
        verbose_name = '销量统计'
        verbose_name_plural = verbose_name
        ordering = ['sale_date']

    def __str__(self):
        return str(self.qty)


class StockReport(models.Model):
    """
    库存统计
    """
    qty = models.IntegerField(default=0, verbose_name='库存量', help_text='库存量')
    amount = models.FloatField(default=0.0, verbose_name='库存金额', help_text='库存金额')
    series = models.CharField(null=True, blank=True, max_length=30, verbose_name='产品系列', help_text='产品系列')
    stock_date = models.DateField(null=True, blank=True, verbose_name='库存日期', help_text='库存日期')

    class Meta:
        verbose_name = '库存统计'
        verbose_name_plural = verbose_name
        ordering = ['stock_date']

    def __str__(self):
        return str(self.qty)


class CustomerReport(models.Model):
    """
    客户销量统计报告
    """
    customer = models.ForeignKey(Customer, null=True, related_name='customer_report',
                                 on_delete=models.CASCADE,
                                 verbose_name='客户', help_text='客户')
    qty = models.IntegerField(default=0, verbose_name='累积购买量', help_text='累积购买量')
    amount = models.FloatField(default=0.0, verbose_name='累积购买金额', help_text='累积购买金额')
    series = models.CharField(null=True, blank=True, max_length=30, verbose_name='产品系列', help_text='产品系列')
    calc_date = models.DateField(null=True, blank=True, verbose_name='统计日期', help_text='统计日期')

    class Meta:
        verbose_name = '客户销量统计报告'
        verbose_name_plural = verbose_name
        ordering = ['-calc_date']

    def __str__(self):
        return str(self.qty)


class ProductReport(models.Model):
    """
    统计产品每天销量
    """
    product = models.ForeignKey(Product, null=True, related_name='product_report',
                                on_delete=models.CASCADE,
                                verbose_name='产品', help_text='产品')
    qty = models.IntegerField(default=0, verbose_name='产品销量', help_text='产品销量')
    amount = models.FloatField(default=0.0, verbose_name='产品销售额', help_text='产品销售额')
    calc_date = models.DateField(null=True, blank=True, verbose_name='统计日期', help_text='统计日期')

    class Meta:
        verbose_name = '统计产品每天销量'
        verbose_name_plural = verbose_name
        ordering = ['-calc_date']

    def __str__(self):
        return str(self.qty)
