from __future__ import absolute_import
from celery import shared_task
from datetime import datetime, timedelta
from django.db.models import Sum
from django.db.models import Q

from product.models import Product
from purchase.models import RefillPromote, PurchaseDetail
from setting.models import TaskLog
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

    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 2
    task_log.note = '销量计算'
    task_log.save()

    return 'OK'


# 计算补货推荐数量
@shared_task()
def calc_refill():
    # 通用参数
    sys_alert_qty = 10  # 警戒库存
    sys_mini_pq = 10  # 最小采购量
    sys_max_pq = 50  # 采购上限
    sys_stock_days = 7  # 备货天数

    # 取出产品 1.在售 2.补货推荐： 开启
    products = Product.objects.filter(status='ON_SALE', is_auto_promote=True)
    for p in products:
        if Stock.objects.filter(product=p).count():
            # 计算该产品所有仓库现有库存之和
            sum_stock = Stock.objects.filter(product=p).aggregate(Sum('qty'))
            ave_stock = sum_stock['qty__sum']  # 现有库存之和
            q = Q()
            q.connector = 'OR'
            q.children.append(('purchase_order__order_status', 'WAIT_CONFIRM'))
            q.children.append(('purchase_order__order_status', 'IN_PRODUCTION'))
            q.children.append(('purchase_order__order_status', 'SENT'))
            # 计算正在采购的数量,状态为 WAIT_CONFIRM，IN_PRODUCTION，SENT采购单中的下单数量 QTY
            sum_qty1 = PurchaseDetail.objects.filter(product=p).filter(q).aggregate(Sum('qty'))
            buy_qty1 = sum_qty1['qty__sum']
            if buy_qty1:
                buy_qty = buy_qty1
            else:
                buy_qty = 0

            # 状态为PART_SENT 采购单中的 下单数量 QTY - 收货数量 Received_qty
            sum_rec1 = PurchaseDetail.objects.filter(product=p).filter(purchase_order__order_status='PART_SENT').aggregate(Sum('qty'))
            sum_rec2 = PurchaseDetail.objects.filter(product=p).filter(purchase_order__order_status='PART_SENT').aggregate(Sum('received_qty'))
            if sum_rec1['qty__sum']:
                rec1 = sum_rec1['qty__sum']
            else:
                rec1 = 0
            if sum_rec2['received_qty__sum']:
                rec2 = sum_rec2['received_qty__sum']
            else:
                rec2 = 0
            buy_qty += (rec1 - rec2)
            # 总库存=现有库存+正在采购数量
            all_stock = ave_stock + buy_qty

            # 计算该产品所有仓库近7天销量之和
            sum_7d = Stock.objects.filter(product=p).aggregate(Sum('recent_7d_sales'))
            all_7d_sold = sum_7d['recent_7d_sales__sum']
            avg_7d = all_7d_sold / 7

            # 计算该产品所有仓库近30天销量之和
            sum_30d = Stock.objects.filter(product=p).aggregate(Sum('recent_30d_sales'))
            all_30d_sold = sum_30d['recent_30d_sales__sum']
            avg_30d = all_30d_sold / 30

            alert_qty = sys_alert_qty
            mini_pq = sys_mini_pq
            max_pq = sys_max_pq
            stock_days = sys_stock_days
            # 如果SKU有设置设警戒库存，以sku数据计算
            if p.alert_qty:
                alert_qty = p.alert_qty
            # 如果SKU有设置最小采购量，以sku数据计算
            if p.mini_pq:
                mini_pq = p.mini_pq
            # 如果SKU有设置采购上限，以sku数据计算
            if p.max_pq:
                max_pq = p.max_pq
            # 如果SKU有设置备货天数，以sku数据计算
            if p.stock_days:
                stock_days = p.stock_days

            # 是否推荐采购，唯一判断条件库存是否低于警戒库存
            if all_stock < alert_qty:
                # 最近7天销量 和 最近30天销量各占50%的比重计算出日均销量
                day_sold = (avg_7d * 0.5) + (avg_30d * 0.5)
                refill_qty = int(day_sold * stock_days)

                # 检查最小采购量和采购上限
                if refill_qty < mini_pq:
                    refill_qty = mini_pq
                if refill_qty > max_pq:
                    refill_qty = max_pq

                # 如果推荐存在，则更新数量，如果不存在，则新建推荐
                if RefillPromote.objects.filter(product=p).count():
                    rp = RefillPromote.objects.filter(product=p).first()
                    rp.qty = refill_qty
                    rp.create_time = datetime.now()
                    rp.save()
                else:
                    refill = RefillPromote()
                    refill.qty = refill_qty
                    refill.product = p
                    refill.save()
            else:
                # 如果产品不符合推荐条件，检查是否已经在推荐列表中，有的话重置推荐数量为0
                if RefillPromote.objects.filter(product=p).count():
                    ref = RefillPromote.objects.filter(product=p).first()
                    ref.qty = 0
                    ref.save()
    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 1
    task_log.note = '补货推荐计算'
    task_log.save()

    return 'OK'
