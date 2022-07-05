from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, post_init

from bonus.models import AccountSales, ExchangeRate


# 账号销售报表保存前处理
@receiver(pre_save, sender=AccountSales)
def account_sales_signal(sender, instance, created=False, **kwargs):
    # ebay平台计算方案
    if instance.platform == 'eBay':
        # 销售净收入 (原始货币)：销售额-ebay费用
        instance.sale_income = instance.sale_amount - instance.platform_fees

        # 结汇收入(人民币)	：结汇扣去2.5%
        instance.FES = instance.receipts * instance.currency_rate * 0.975

        #  毛利润(提成利润)
        instance.profit = instance.FES - instance.product_cost - instance.shipping_cost

        # 当月毛利润
        instance.month_profit = instance.sale_income * instance.currency_rate - instance.product_cost - instance.shipping_cost

        #  毛利率
        instance.profit_margin = instance.month_profit / (instance.sale_amount * instance.currency_rate)

        # 客单价
        instance.CUP = instance.sale_amount / instance.orders

        #  广告费占比
        instance.ad_percent = instance.ad_fees / instance.sale_amount

        #  平台费用 (rmb)
        instance.platform_fees_rmb = instance.platform_fees * instance.currency_rate

        #  广告费(rmb)
        instance.ad_fees_rmb = instance.ad_fees * instance.currency_rate
    # Aliexpress平台计算方案
    if instance.platform == 'Aliexpress':
        # 销售净收入 (原始货币)：销售额-Aliexpress费用
        instance.sale_income = instance.sale_amount - instance.platform_fees

        # 结汇收入(人民币)	：结汇扣去2.5%
        instance.FES = instance.receipts * instance.currency_rate * 0.975
        #  广告费(rmb)
        instance.ad_fees_rmb = instance.ad_fees * instance.currency_rate

        #  毛利润(提成利润)
        instance.profit = instance.FES - instance.product_cost - instance.shipping_cost - instance.ad_fees_rmb

        # 当月毛利润
        instance.month_profit = instance.sale_income * instance.currency_rate - instance.product_cost - instance.shipping_cost - instance.ad_fees_rmb

        #  毛利率
        instance.profit_margin = instance.month_profit / (instance.sale_amount * instance.currency_rate)

        # 客单价
        instance.CUP = instance.sale_amount / instance.orders

        #  广告费占比
        instance.ad_percent = instance.ad_fees / instance.sale_amount

        #  平台费用 (rmb)
        instance.platform_fees_rmb = instance.platform_fees * instance.currency_rate

    # coupang平台计算方案
    if instance.platform == 'Coupang':
        #  毛利润
        instance.profit = instance.FES - instance.product_cost - instance.cp_first_ship
        instance.month_profit = instance.profit


# 汇率变动
@receiver(post_save, sender=ExchangeRate)
def exchange_rate_signal(sender, instance, created, **kwargs):
    if not created:
        # 修改销售报表汇率
        if instance.__original_rate != instance.rate:
            queryset = AccountSales.objects.filter(ori_currency=instance.currency, month=instance.month)
            for i in queryset:
                i.currency_rate = instance.rate
                i.save()


# 汇率变动，获取原数据
@receiver(post_init, sender=ExchangeRate)
def exchange_rate_init_signal(instance, **kwargs):
    instance.__original_rate = instance.rate
