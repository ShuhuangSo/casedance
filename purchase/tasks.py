from __future__ import absolute_import
from celery import shared_task
from datetime import datetime, timedelta
from django.db.models import Sum

from store.models import Stock, StockLog


@shared_task
# 定义的定时任务函数
def auto_sc():
    print('测试任务～～～')
    return 'halo'


# 计算产品卖出数量
@shared_task()
def calc_sold_qty():
    dt_e = datetime.now()
    dt_s_7 = (datetime.now().date() - timedelta(days=7))
    dt_s_30 = (datetime.now().date() - timedelta(days=30))

    queryset = Stock.objects.all()
    for stock in queryset:
        # 查询今天+过去7天销量
        all_sold_7d = StockLog.objects.filter(create_time__range=[dt_s_7, dt_e],
                                              store=stock.store,
                                              product=stock.product,
                                              op_type='S_OUT')
        if all_sold_7d.count():
            sold_7_days = all_sold_7d.aggregate(Sum('qty'))
            stock.recent_7d_sales = sold_7_days['qty__sum']

        # 查询今天+过去30天销量
        all_sold_30d = StockLog.objects.filter(create_time__range=[dt_s_30, dt_e],
                                               store=stock.store,
                                               product=stock.product,
                                               op_type='S_OUT')
        if all_sold_30d.count():
            sold_30_days = all_sold_30d.aggregate(Sum('qty'))
            stock.recent_30d_sales = sold_30_days['qty__sum']

        # 查询最后销售时间
        last_sold = StockLog.objects.filter(store=stock.store,
                                            product=stock.product,
                                            op_type='S_OUT').last()
        if last_sold:
            last_sold_time = last_sold.create_time
            stock.last_sale_time = last_sold_time

        stock.save()

    return 'OK'
