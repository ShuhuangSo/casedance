from __future__ import absolute_import
from celery import shared_task
from datetime import datetime, timedelta


# 计算客户购买量报告
from product.models import ProductExtraInfo
from report.models import CustomerReport
from sale.models import Customer, OrderDetail


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
    return 'OK'
