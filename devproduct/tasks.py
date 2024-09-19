from __future__ import absolute_import
from celery import shared_task
from django.db.models import Sum, Avg, Q
from datetime import datetime, timedelta

from devproduct.models import DevOrder, DevProduct, DevListingAccount
from setting.models import TaskLog
from casedance.settings import MEDIA_ROOT
from mercado.models import FileUploadNotify


# 计算开发产品销量
@shared_task
def calc_product_sales():

    p_list = DevProduct.objects.filter(p_status='ONLINE')
    for i in p_list:
        # 7天销量 # 排除重发订单
        day7 = datetime.now().date() - timedelta(days=7)
        sum_day7 = DevOrder.objects.filter(sku=i.sku,
                                           is_resent=False,
                                           order_time__gte=day7).aggregate(
                                               Sum('qty'))
        day7_sold = sum_day7['qty__sum']
        # 15天销量 # 排除重发订单
        day15 = datetime.now().date() - timedelta(days=15)
        sum_day15 = DevOrder.objects.filter(sku=i.sku,
                                            is_resent=False,
                                            order_time__gte=day15).aggregate(
                                                Sum('qty'))
        day15_sold = sum_day15['qty__sum']
        # 30天销量 # 排除重发订单
        day30 = datetime.now().date() - timedelta(days=30)
        sum_day30 = DevOrder.objects.filter(sku=i.sku,
                                            is_resent=False,
                                            order_time__gte=day30).aggregate(
                                                Sum('qty'))
        day30_sold = sum_day30['qty__sum']
        # 累计销量 # 排除重发订单
        sum_total = DevOrder.objects.filter(sku=i.sku,
                                            is_resent=False).aggregate(
                                                Sum('qty'))
        total_sold = sum_total['qty__sum']

        # 累计利润
        sum_profit = DevOrder.objects.filter(sku=i.sku,
                                             is_settled=True).aggregate(
                                                 Sum('profit'))
        total_profit = sum_profit['profit__sum']
        # 平均毛利润
        avg_profit = DevOrder.objects.filter(sku=i.sku,
                                             is_settled=True).aggregate(
                                                 Avg('profit'))
        avg_profit = avg_profit['profit__avg']
        # 平均毛利率
        a_profit_rate = DevOrder.objects.filter(sku=i.sku,
                                                is_settled=True).aggregate(
                                                    Avg('profit_rate'))
        avg_profit_rate = a_profit_rate['profit_rate__avg']

        i.day15_sold = day15_sold if day15_sold else 0
        i.day7_sold = day7_sold if day7_sold else 0
        i.day30_sold = day30_sold if day30_sold else 0
        i.total_sold = total_sold if total_sold else 0
        i.total_profit = total_profit if sum_profit else 0
        i.avg_profit = avg_profit if avg_profit else 0
        i.avg_profit_rate = avg_profit_rate if avg_profit_rate else 0
        i.save()
    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 14
    task_log.note = '开发产品销量计算'
    task_log.save()

    return 'OK'


# 上传订单
@shared_task()
def upload_dev_order(notify_id):
    import warnings
    import openpyxl
    warnings.filterwarnings('ignore')

    data = MEDIA_ROOT + '/upload_file/dev_order_excel.xlsx'
    wb = openpyxl.load_workbook(data)
    sheet = wb.active
    file_upload = FileUploadNotify.objects.filter(id=notify_id).first()
    if sheet.max_row <= 1:
        file_upload.upload_status = 'ERROR'
        file_upload.desc = '表格不能为空!'
        file_upload.save()
        return 'ERROR'
    if sheet['A1'].value != '订单编号':
        file_upload.upload_status = 'ERROR'
        file_upload.desc = '模板格式有误，请检查!'
        file_upload.save()
        return 'ERROR'

    c_num = 0  # 空单号标记码
    for cell_row in list(sheet)[1:]:
        order_number = cell_row[0].value
        account_name = cell_row[1].value
        platform = cell_row[2].value
        if platform == 'ebay':
            platform = 'eBay'
        site = cell_row[3].value
        if site == 'GB':
            site = 'UK'
        currency = cell_row[4].value
        sku = cell_row[5].value
        qty = cell_row[6].value
        if not type(qty) in [float, int]:
            if qty:
                qty = int(qty)
            else:
                qty = 0
        item_price = cell_row[7].value
        if not type(item_price) in [float, int]:
            if item_price:
                item_price = float(item_price)
            else:
                item_price = 0
        postage_price = cell_row[8].value
        if not type(postage_price) in [float, int]:
            if postage_price:
                postage_price = float(postage_price)
            else:
                postage_price = 0
        total_price = cell_row[9].value
        if not type(total_price) in [float, int]:
            if total_price:
                total_price = float(total_price)
            else:
                total_price = 0
        postage = cell_row[10].value
        if not type(postage) in [float, int]:
            if postage:
                postage = float(postage)
            else:
                postage = 0
        profit = cell_row[11].value
        if not type(profit) in [float, int]:
            if profit:
                profit = float(profit)
            else:
                profit = 0
        profit_rate = cell_row[12].value
        if not type(profit_rate) in [float, int]:
            if profit_rate:
                profit_rate = float(profit_rate.replace('%', '')) / 100
            else:
                profit_rate = 0
        ad_fee = cell_row[13].value
        if not type(ad_fee) in [float, int]:
            if ad_fee:
                ad_fee = float(ad_fee)
            else:
                ad_fee = 0
        item_id = cell_row[14].value
        order_time = cell_row[15].value
        is_resent = False if cell_row[16].value == '否' else True
        ex_rate = cell_row[17].value
        if not type(ex_rate) in [float, int]:
            if ex_rate:
                ex_rate = float(ex_rate)
            else:
                ex_rate = 0

        is_exist = DevOrder.objects.filter(order_number=order_number).count()
        # 订单号已存在情况
        if is_exist:
            # 合并订单的条数
            if order_number:
                c_num = is_exist - 1
            if postage:
                if is_exist == 1:
                    od = DevOrder.objects.filter(
                        order_number=order_number).first()
                    # 未结算订单
                    if not od.is_settled:
                        od.postage = postage
                        od.profit = profit
                        od.profit_rate = profit_rate
                        od.is_settled = True
                        od.save()
                if is_exist > 1:
                    # 合并订单情况
                    od_list = DevOrder.objects.filter(
                        order_number=order_number)
                    for i in od_list:
                        # 未结算订单
                        if not i.is_settled:
                            i.postage = postage
                            i.profit = profit
                            i.profit_rate = profit_rate
                            i.is_settled = True
                            i.save()

            continue

        # 判断该无单号行是新订单还是重复订单
        if not order_number:
            if c_num:
                c_num -= 1
                continue
        if order_number and sku:
            dp = DevProduct.objects.filter(sku=sku).first()
            if dp:
                # 创建订单
                od = DevOrder()
                od.dev_p_id = dp.id
                od.unit_cost = dp.unit_cost
                od.sku = dp.sku
                od.cn_name = dp.cn_name
                od.image = dp.image
                od.order_number = order_number
                od.platform = platform
                od.site = site
                od.account_name = account_name
                od.currency = currency
                od.qty = qty
                od.item_price = item_price
                od.item_id = item_id
                od.postage_price = postage_price
                od.total_price = total_price
                od.postage = postage
                od.is_settled = True if postage else False  # 有发货运费则视为已结算
                od.profit = profit if postage else 0
                od.profit_rate = profit_rate if postage else 0
                od.ad_fee = ad_fee
                od.is_ad = True if ad_fee else False
                od.order_time = order_time
                od.is_resent = is_resent
                od.ex_rate = ex_rate
                od.save()
                # 账号销量记录
                # 不计算重发订单
                if not od.is_resent:
                    dla = DevListingAccount.objects.filter(
                        dev_p=dp, account_name=account_name).first()
                    if dla:
                        dla.total_sold += qty
                        dla.save()
        elif not order_number and sku:
            # 合并订单产品
            dp = DevProduct.objects.filter(sku=sku).first()
            if dp:
                last_order = DevOrder.objects.order_by('id').last()
                # 创建订单
                od = DevOrder()
                od.dev_p_id = dp.id
                od.unit_cost = dp.unit_cost
                od.sku = dp.sku
                od.cn_name = dp.cn_name
                od.image = dp.image
                od.order_number = last_order.order_number
                od.platform = last_order.platform
                od.site = last_order.site
                od.account_name = last_order.account_name
                od.currency = last_order.currency
                od.qty = qty
                od.item_price = item_price
                od.item_id = item_id
                od.postage_price = last_order.postage_price
                od.total_price = last_order.total_price
                od.postage = last_order.postage
                od.is_settled = last_order.is_settled
                od.profit = last_order.profit
                od.profit_rate = last_order.profit_rate
                od.ad_fee = last_order.ad_fee
                od.is_ad = last_order.is_ad
                od.order_time = last_order.order_time
                od.is_resent = last_order.is_resent
                od.is_combined = True  # 合并订单
                od.ex_rate = last_order.ex_rate
                od.save()
                last_order.is_combined = True
                last_order.save()
                # 账号销量记录
                # 不计算重发订单
                if not od.is_resent:
                    dla = DevListingAccount.objects.filter(
                        dev_p=dp, account_name=account_name).first()
                    if dla:
                        dla.total_sold += qty
                        dla.save()
        else:
            continue
    # 修改上传通知
    file_upload.upload_status = 'SUCCESS'
    file_upload.desc = '上传成功!'
    file_upload.save()
    return 'SUCESS'
