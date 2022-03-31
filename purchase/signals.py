from django.db.models.signals import post_save, post_init, post_delete
from django.dispatch import receiver

from setting.models import OperateLog
from store.models import Stock

import inspect

from purchase.models import PurchaseDetail, PurchaseOrder, PurchaseOrderTag


# 采购单详情，检测有增量的收货库存数量，则增加库存
@receiver(post_save, sender=PurchaseDetail)
def purchase_detail_signal(sender, instance, created, **kwargs):
    # 获取当前user
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None

    if not created:
        # 收货产品入库操作
        add_stock = instance.received_qty - instance.__original_received_qty  # 增加的收货数量，用于入库
        if add_stock:
            stock = Stock.objects.filter(store=instance.purchase_order.store).get(product=instance.product)
            stock.qty += add_stock
            stock.save()

        # 操作日志记录
        str_list = []
        if instance.__original_received_qty != instance.received_qty:
            str_list.append('%s新增入库数量： %s' % (instance.product.sku, add_stock))
        if instance.__original_qty != instance.qty:
            str_list.append('%s采购数量: %s ===>> %s' % (instance.product.sku, instance.__original_qty, instance.qty))
        if instance.__original_unit_cost != instance.unit_cost:
            str_list.append('%s采购价格: %s ===>> %s' % (instance.product.sku, instance.__original_unit_cost, instance.unit_cost))
        if instance.__original_is_supply_case != instance.is_supply_case:
            str_list.append('%s是否提供素材壳: %s ===>> %s' % (instance.product.sku, instance.__original_is_supply_case, instance.is_supply_case))
        if instance.__original_sent_qty != instance.sent_qty:
            str_list.append('%s新增发货数量: %s' % (instance.product.sku, instance.sent_qty - instance.__original_sent_qty))
        if instance.__original_paid_qty != instance.paid_qty:
            str_list.append('%s新增结算数量: %s' % (instance.product.sku, instance.paid_qty - instance.__original_paid_qty))
        if instance.__original_short_note != instance.short_note:
            str_list.append('%s备注: %s ===>> %s' % (instance.product.sku, instance.__original_short_note, instance.short_note))

        if str_list:
            op = OperateLog()
            if request:
                op.user = request.user
            op.op_log = '; '.join(str_list)
            op.op_type = 'PURCHASE'
            op.target_id = instance.purchase_order.id
            op.save()

    if created:
        op = OperateLog()
        if request:
            op.user = request.user
        op.op_log = '增加了新sku：%s , 数量：%s, 单价：%s, 是否提供素材壳：%s, 备注：%s' % (instance.product.sku, instance.qty, instance.unit_cost, instance.is_supply_case, instance.short_note)
        op.op_type = 'PURCHASE'
        op.target_id = instance.purchase_order.id
        op.save()


# 记录删除采购单详情产品的操作日志
@receiver(post_delete, sender=PurchaseDetail)
def product_detail_delete_signal(sender, instance, **kwargs):
    # 获取当前user
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None

    op = OperateLog()
    if request:
        op.user = request.user
    op.op_log = '删除sku：' + instance.product.sku
    op.op_type = 'PURCHASE'
    op.target_id = instance.purchase_order.id
    op.save()


# 采购单详情，获取原数据
@receiver(post_init, sender=PurchaseDetail)
def purchase_detail_init_signal(instance, **kwargs):
    instance.__original_received_qty = instance.received_qty
    instance.__original_qty = instance.qty
    instance.__original_unit_cost = instance.unit_cost
    instance.__original_sent_qty = instance.sent_qty
    instance.__original_is_supply_case = instance.is_supply_case
    instance.__original_paid_qty = instance.paid_qty
    instance.__original_short_note = instance.short_note


# 记录采购单操作日志
@receiver(post_save, sender=PurchaseOrder)
def purchase_order_signal(sender, instance, created, **kwargs):
    # 获取当前user
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None

    if created:
        op = OperateLog()
        if request:
            op.user = request.user
        op.op_log = '创建了采购单'
        op.op_type = 'PURCHASE'
        op.target_id = instance.id
        op.save()
    else:
        # 记录修改操作日志
        str_list = []
        if instance.__original_store != instance.store:
            str_list.append('仓库/门店: %s ===>> %s' % (instance.__original_store, instance.store))
        if instance.__original_supplier != instance.supplier:
            str_list.append('供应商: %s ===>> %s' % (instance.__original_supplier, instance.supplier))
        if instance.__original_logistic != instance.logistic:
            if not instance.__original_logistic:
                str_list.append('新增物流公司： %s' % instance.logistic)
            else:
                str_list.append('物流公司: %s ===>> %s' % (instance.__original_logistic, instance.logistic))
        if instance.__original_tracking_number != instance.tracking_number:
            if not instance.__original_tracking_number:
                str_list.append('新增物流单号： %s' % instance.tracking_number)
            else:
                str_list.append('物流单号: %s ===>> %s' % (instance.__original_tracking_number, instance.tracking_number))
        if instance.__original_postage != instance.postage:
            str_list.append('运费: %s ===>> %s' % (instance.__original_postage, instance.postage))
        if instance.__original_note != instance.note:
            str_list.append('备注: %s ===>> %s' % (instance.__original_note, instance.note))
        if instance.__original_paid_status != instance.paid_status:
            if instance.paid_status == 'PART_PAID':
                str_list.append('采购单进行部分结算')
            if instance.paid_status == 'FULL_PAID':
                str_list.append('采购单已全部结算')
        if instance.__original_order_status != instance.order_status:
            if instance.order_status == 'CANCEL':
                str_list.append('采购单作废')
            if instance.order_status == 'WAIT_CONFIRM':
                str_list.append('采购单已发送给供应商')
            if instance.order_status == 'IN_PRODUCTION':
                str_list.append('供应商已确认')
            if instance.order_status == 'SENT':
                str_list.append('供应商已发货')
            if instance.order_status == 'PART_SENT':
                str_list.append('供应商部分发货')
            if instance.order_status == 'FINISHED':
                str_list.append('采购单已完成')

        if str_list:
            op = OperateLog()
            if request:
                op.user = request.user
            op.op_log = '; '.join(str_list)
            op.op_type = 'PURCHASE'
            op.target_id = instance.id
            op.save()


# 采购单数据保存前的初始化，将原数据保存起来
@receiver(post_init, sender=PurchaseOrder)
def purchase_order_init_signal(instance, **kwargs):
    instance.__original_store = instance.store
    instance.__original_supplier = instance.supplier
    instance.__original_logistic = instance.logistic
    instance.__original_tracking_number = instance.tracking_number
    instance.__original_postage = instance.postage
    instance.__original_note = instance.note
    instance.__original_paid_status = instance.paid_status
    instance.__original_order_status = instance.order_status


# 记录新增采购单标签的操作日志
@receiver(post_save, sender=PurchaseOrderTag)
def purchase_order_tag_create_signal(sender, instance, created, **kwargs):
    # 获取当前user
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None

    if created:
        op = OperateLog()
        if request:
            op.user = request.user
        op.op_log = '增加标签：' + instance.tag.tag_name
        op.op_type = 'PURCHASE'
        op.target_id = instance.purchase_order.id
        op.save()


# 记录删除采购单标签的操作日志
@receiver(post_delete, sender=PurchaseOrderTag)
def product_tag_delete_signal(sender, instance, **kwargs):
    # 获取当前user
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None

    op = OperateLog()
    if request:
        op.user = request.user
    op.op_log = '删除标签：' + instance.tag.tag_name
    op.op_type = 'PURCHASE'
    op.target_id = instance.purchase_order.id
    op.save()