from __future__ import absolute_import
from celery import shared_task
from datetime import datetime, timedelta
from django.db.models import Q

from product.models import ProductExtraInfo, Product
from report.models import CustomerReport, ProductReport, SalesReport
from sale.models import Customer, OrderDetail


# 计算客户购买量报告
from setting.models import TaskLog


@shared_task()
def calc_customer_report():
    customers = Customer.objects.filter(is_active=True)
    # 计算所有客户60天的销量数据
    for cus in customers:
        add_list = []
        for i in range(60):
            date = datetime.now().date() - timedelta(days=i)
            series_set = ProductExtraInfo.objects.filter(type='SERIES')
            for s in series_set:
                order_set = OrderDetail.objects.filter(order__create_time__date=date,
                                                       order__customer=cus,
                                                       order__order_status='FINISHED',
                                                       product__series=s.name)
                qty = 0
                amount = 0.0
                for item in order_set:
                    qty += item.qty
                    amount += item.qty * item.sold_price

                cr = CustomerReport.objects.filter(calc_date=date, series=s.name, customer=cus).first()
                if cr:
                    cr.qty = qty
                    cr.amount = amount
                    cr.save()
                else:
                    add_list.append(CustomerReport(
                        qty=qty,
                        amount=amount,
                        series=s.name,
                        customer=cus,
                        calc_date=date
                    ))
        if len(add_list):
            CustomerReport.objects.bulk_create(add_list)
    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 6
    task_log.note = '客户60天采购量计算'
    task_log.save()
    return '客户60天采购量计算'


# 计算sku产品60天每天销量
@shared_task()
def calc_product_sale():

    q = Q()
    q.connector = 'OR'
    q.children.append(('status', 'ON_SALE'))
    q.children.append(('status', 'CLEAN'))
    q.children.append(('status', 'PRIVATE'))
    products = Product.objects.filter(q)
    for p in products:
        add_list = []
        for i in range(60):
            date = datetime.now().date() - timedelta(days=i)
            order_set = OrderDetail.objects.filter(order__create_time__date=date,
                                                   order__order_status='FINISHED',
                                                   product=p)
            qty = 0
            amount = 0.0
            for item in order_set:
                qty += item.qty
                amount += item.qty * item.sold_price

            pr = ProductReport.objects.filter(calc_date=date, product=p).first()
            if pr:
                pr.qty = qty
                pr.amount = amount
                pr.save()
            else:
                add_list.append(ProductReport(
                    qty=qty,
                    amount=amount,
                    product=p,
                    calc_date=date
                ))
        if len(add_list):
            ProductReport.objects.bulk_create(add_list)
    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 7
    task_log.note = '每sku每天销量计算'
    task_log.save()
    return '每sku每天销量计算'


# 计算产品60天每天累积总销量
@shared_task()
def calc_total_sale():
    add_list = []
    for i in range(60):
        date = datetime.now().date() - timedelta(days=i + 1)  # from yesterday

        series_set = ProductExtraInfo.objects.filter(type='SERIES')
        for s in series_set:
            order_set = OrderDetail.objects.filter(order__create_time__date=date,
                                                   order__order_status='FINISHED',
                                                   product__series=s.name)
            qty = 0
            amount = 0.0
            for item in order_set:
                qty += item.qty
                amount += item.qty * item.sold_price

            sr = SalesReport.objects.filter(sale_date=date, series=s.name).first()
            if sr:
                sr.qty = qty
                sr.amount = amount
                sr.save()
            else:
                add_list.append(SalesReport(
                    qty=qty,
                    amount=amount,
                    series=s.name,
                    sale_date=date
                ))
    if len(add_list):
        SalesReport.objects.bulk_create(add_list)
    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 5
    task_log.note = '过去60天总销量计算'
    task_log.save()
    return '60天总销量已计算'