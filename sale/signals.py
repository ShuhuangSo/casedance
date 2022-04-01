import time
from random import Random
import inspect

from django.db.models.signals import pre_save, post_save, post_init, post_delete
from django.dispatch import receiver

from sale.models import Customer, CustomerDiscount, CustomerTag, Order, OrderDetail, OrderTag
from setting.models import OperateLog


# 客户创建前生成客户代码并保存
from store.models import Stock


@receiver(pre_save, sender=Customer)
def customer_code_signal(sender, instance, created=False, **kwargs):
    if instance._state.adding:  # 判断是否create
        # 获取不重复的客户代码
        if Customer.objects.all().count():
            cus_id = Customer.objects.first().id
        else:
            cus_id = 1
        random_ins = Random()
        code = 'C{time_str}{ranstr}{cus_id}'.format(time_str=time.strftime('%Y%m'),
                                                    ranstr=random_ins.randint(10, 99), cus_id=cus_id)
        instance.customer_code = code


# 客户资料操作日志记录
@receiver(post_save, sender=Customer)
def customer_signal(sender, instance, created, **kwargs):
    # 获取当前user
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None

    if not created:
        # 记录修改操作日志
        str_list = []
        if instance.__original_company_name != instance.company_name:
            str_list.append('公司名称: %s ===>> %s' % (instance.__original_company_name, instance.company_name))
        if instance.__original_pay_way != instance.pay_way:
            str_list.append('结算类型: %s ===>> %s' % ('现结' if instance.__original_pay_way == 'PAY_NOW' else '约定付款',
                                                   '现结' if instance.pay_way == 'PAY_NOW' else '约定付款'))
        if instance.__original_address != instance.address:
            str_list.append('地址: %s ===>> %s' % (instance.__original_address, instance.address))
        if instance.__original_contact_name != instance.contact_name:
            str_list.append('联系人: %s ===>> %s' % (instance.__original_contact_name, instance.contact_name))
        if instance.__original_phone != instance.phone:
            str_list.append('手机: %s ===>> %s' % (instance.__original_phone, instance.phone))
        if instance.__original_qq != instance.qq:
            str_list.append('QQ: %s ===>> %s' % (instance.__original_qq, instance.qq))
        if instance.__original_wechat != instance.wechat:
            str_list.append('微信: %s ===>> %s' % (instance.__original_wechat, instance.wechat))
        if instance.__original_email != instance.email:
            str_list.append('邮箱: %s ===>> %s' % (instance.__original_email, instance.email))
        if instance.__original_is_active != instance.is_active:
            str_list.append('状态: %s ===>> %s' % ('启用' if instance.__original_is_active else '不启用',
                                                 '启用' if instance.is_active else '不启用'))
        if instance.__original_note != instance.note:
            str_list.append('备注: %s ===>> %s' % (instance.__original_note, instance.note))
        if instance.__original_level != instance.level:
            str_list.append('客户评级: %s ===>> %s' % (instance.__original_level, instance.level))
        if str_list:
            op = OperateLog()
            if request:
                op.user = request.user
            op.op_log = '; '.join(str_list)
            op.op_type = 'CUSTOMER'
            op.target_id = instance.id
            op.save()
    else:
        op = OperateLog()
        if request:
            op.user = request.user
        op.op_log = '创建了客户'
        op.op_type = 'CUSTOMER'
        op.target_id = instance.id
        op.save()


# 客户资料操作日志记录，获取原数据
@receiver(post_init, sender=Customer)
def customer_init_signal(instance, **kwargs):
    instance.__original_company_name = instance.company_name
    instance.__original_pay_way = instance.pay_way
    instance.__original_address = instance.address
    instance.__original_contact_name = instance.contact_name
    instance.__original_phone = instance.phone
    instance.__original_qq = instance.qq
    instance.__original_wechat = instance.wechat
    instance.__original_email = instance.email
    instance.__original_is_active = instance.is_active
    instance.__original_note = instance.note
    instance.__original_level = instance.level


# 客户专属优惠操作日志记录
@receiver(post_save, sender=CustomerDiscount)
def customer_discount_signal(sender, instance, created, **kwargs):
    # 获取当前user
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None

    if not created:
        # 记录修改操作日志
        str_list = []
        if instance.__original_discount_type != instance.discount_type:
            str_list.append('%s 系列折扣类型: %s ===>> %s' % (
                instance.p_series,
                '金额数' if instance.__original_discount_type else '百分比',
                '金额数' if instance.discount_type else '百分比'))
        if instance.__original_discount_money != instance.discount_money:
            str_list.append('%s 系列折扣金额: %s ===>> %s' % (
                instance.p_series, instance.__original_discount_money, instance.discount_money))
        if instance.__original_discount_percent != instance.discount_percent:
            str_list.append('%s 系列折扣比例: %s ===>> %s' % (
                instance.p_series, instance.__original_discount_percent, instance.discount_percent))
        if str_list:
            op = OperateLog()
            if request:
                op.user = request.user
            op.op_log = '; '.join(str_list)
            op.op_type = 'CUSTOMER'
            op.target_id = instance.customer.id
            op.save()
    else:
        op = OperateLog()
        if request:
            op.user = request.user
        op.op_log = '增加了 %s 系列折扣,折扣类型： %s ,折扣金额: %s,折扣比例: %s' % (
            instance.p_series,
            '金额数' if instance.discount_type else '百分比',
            instance.discount_money,
            instance.discount_percent)
        op.op_type = 'CUSTOMER'
        op.target_id = instance.customer.id
        op.save()


# 记录删除客户专属优惠签的操作日志
@receiver(post_delete, sender=CustomerDiscount)
def customer_discount_delete_signal(sender, instance, **kwargs):
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
    op.op_log = '删除了 %s 系列折扣,折扣类型： %s ,折扣金额: %s,折扣比例: %s' % (
        instance.p_series,
        '金额数' if instance.discount_type else '百分比',
        instance.discount_money,
        instance.discount_percent)
    op.op_type = 'CUSTOMER'
    op.target_id = instance.customer.id
    op.save()


# 客户专属优惠操作日志记录，获取原数据
@receiver(post_init, sender=CustomerDiscount)
def customer_discount_init_signal(instance, **kwargs):
    instance.__original_discount_type = instance.discount_type
    instance.__original_discount_money = instance.discount_money
    instance.__original_discount_percent = instance.discount_percent


# 记录新增客户标签的操作日志
@receiver(post_save, sender=CustomerTag)
def customer_tag_create_signal(sender, instance, created, **kwargs):
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
        op.op_type = 'CUSTOMER'
        op.target_id = instance.customer.id
        op.save()


# 记录删除客户标签的操作日志
@receiver(post_delete, sender=CustomerTag)
def customer_tag_delete_signal(sender, instance, **kwargs):
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
    op.op_type = 'CUSTOMER'
    op.target_id = instance.customer.id
    op.save()


# 销售单资料操作日志记录，获取原数据
@receiver(post_init, sender=Order)
def order_init_signal(instance, **kwargs):
    instance.__original_store = instance.store
    instance.__original_customer = instance.customer
    instance.__original_address = instance.address
    instance.__original_contact_name = instance.contact_name
    instance.__original_phone = instance.phone
    instance.__original_order_type = instance.order_type
    instance.__original_order_status = instance.order_status
    instance.__original_pay_way = instance.pay_way
    instance.__original_is_active = instance.is_active
    instance.__original_note = instance.note
    instance.__original_paid_status = instance.paid_status
    instance.__original_logistic = instance.logistic
    instance.__original_tracking_number = instance.tracking_number
    instance.__original_postage = instance.postage


# 记录销售单操作日志, 销售单状态变化后库存的锁定与解锁
@receiver(post_save, sender=Order)
def order_signal(sender, instance, created, **kwargs):
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
        op.op_log = '创建了销售单'
        op.op_type = 'ORDER'
        op.target_id = instance.id
        op.save()
    else:
        # 如果销售单的状态 备货中转为已备货，则进行库存锁定
        if instance.__original_order_status == 'PREPARING' and instance.order_status == 'READY':
            queryset = OrderDetail.objects.filter(order=instance)
            for i in queryset:
                stock = Stock.objects.filter(store=instance.store).get(product=i.product)
                stock.lock_qty += i.qty
                stock.save()
        # 如果销售单的状态 已备货转为备货中，则进行库存解锁
        if instance.__original_order_status == 'READY' and instance.order_status == 'PREPARING':
            queryset = OrderDetail.objects.filter(order=instance)
            for i in queryset:
                stock = Stock.objects.filter(store=instance.store).get(product=i.product)
                stock.lock_qty -= i.qty
                stock.save()

        # 如果销售单的状态 部分发货转为异常，则进行未发货产品库存解锁
        if instance.__original_order_status == 'PART_SENT' and instance.order_status == 'EXCEPTION':
            queryset = OrderDetail.objects.filter(order=instance)
            for i in queryset:
                stock = Stock.objects.filter(store=instance.store).get(product=i.product)
                if i.qty - i.sent_qty:
                    stock.lock_qty -= (i.qty - i.sent_qty)
                    stock.save()

        # 如果销售单的状态 为FINISHED，则直接进行产品库存扣除,不经过发货流程-- POS模式
        if instance.mode == 'POS' and instance.order_status == 'FINISHED':
            queryset = OrderDetail.objects.filter(order=instance)
            for i in queryset:
                stock = Stock.objects.filter(store=instance.store).get(product=i.product)
                stock.qty -= i.qty
                stock.save()

        # 记录修改操作日志
        str_list = []
        if instance.__original_store != instance.store:
            str_list.append('仓库/门店: %s ===>> %s' % (instance.__original_store, instance.store))
        if instance.__original_customer != instance.customer:
            str_list.append('客户: %s ===>> %s' % (instance.__original_customer, instance.customer))
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
        if instance.__original_address != instance.address:
            str_list.append('收货地址: %s ===>> %s' % (instance.__original_address, instance.address))
        if instance.__original_contact_name != instance.contact_name:
            str_list.append('收货人: %s ===>> %s' % (instance.__original_contact_name, instance.contact_name))
        if instance.__original_phone != instance.phone:
            str_list.append('电话: %s ===>> %s' % (instance.__original_phone, instance.phone))
        if instance.__original_order_type != instance.order_type:
            if instance.__original_order_type == 'PICKUP':
                old = '门店自提'
            if instance.__original_order_type == 'EXPRESS':
                old = '快递'
            if instance.__original_order_type == 'SELLER_SEND':
                old = '卖家送货'
            if instance.order_type == 'PICKUP':
                new = '门店自提'
            if instance.order_type == 'EXPRESS':
                new = '快递'
            if instance.order_type == 'SELLER_SEND':
                new = '卖家送货'
            str_list.append('订单类型: %s ===>> %s' % (old, new))
        if instance.__original_pay_way != instance.pay_way:
            str_list.append('结算类型: %s ===>> %s' % ('现结' if instance.__original_pay_way == 'PAY_NOW' else '约定付款',
                                                   '现结' if instance.pay_way == 'PAY_NOW' else '约定付款'))
        if instance.__original_is_active != instance.is_active:
            str_list.append('状态: %s ===>> %s' % (instance.__original_is_active, instance.is_active))
        if instance.__original_paid_status != instance.paid_status:
            if instance.paid_status == 'PART_PAID':
                str_list.append('订单进行部分结算')
            if instance.paid_status == 'FULL_PAID':
                str_list.append('订单已全部结算')
        if instance.__original_order_status != instance.order_status:
            if instance.order_status == 'CANCEL':
                str_list.append('订单作废')
            if instance.order_status == 'PREPARING':
                str_list.append('订单放入草稿箱')
            if instance.order_status == 'READY':
                str_list.append('订单已完成备货')
            if instance.order_status == 'PART_SENT':
                str_list.append('订单已标记部分发货')
            if instance.order_status == 'FINISHED':
                str_list.append('订单已完成')
            if instance.order_status == 'EXCEPTION':
                str_list.append('订单标记异常完成')

        if str_list:
            op = OperateLog()
            if request:
                op.user = request.user
            op.op_log = '; '.join(str_list)
            op.op_type = 'ORDER'
            op.target_id = instance.id
            op.save()


# 销售单产品明细，获取原数据
@receiver(post_init, sender=OrderDetail)
def order_detail_init_signal(instance, **kwargs):
    instance.__original_qty = instance.qty
    instance.__original_unit_price = instance.unit_price
    instance.__original_sold_price = instance.sold_price
    instance.__original_sent_qty = instance.sent_qty
    instance.__original_paid_qty = instance.paid_qty


# 销售单产品明细，日志记录，库存出库检测
@receiver(post_save, sender=OrderDetail)
def order_detail_signal(sender, instance, created, **kwargs):
    # 获取当前user
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None

    # 检测有增量的发货数量，则减去库存,减锁仓量
    if not created:
        # 订单产品出库操作
        reduce_stock = instance.sent_qty - instance.__original_sent_qty  # 增加的发货数量，用于出库
        if reduce_stock:
            stock = Stock.objects.filter(store=instance.order.store).get(product=instance.product)
            stock.qty -= reduce_stock
            stock.lock_qty -= reduce_stock
            stock.save()

        # 操作日志记录
        str_list = []
        if instance.__original_qty != instance.qty:
            str_list.append('%s 数量: %s ===>> %s' % (instance.product.sku, instance.__original_qty, instance.qty))
        if instance.__original_unit_price != instance.unit_price:
            str_list.append('%s原价格: %s ===>> %s' % (instance.product.sku, instance.__original_unit_price, instance.unit_price))
        if instance.__original_sold_price != instance.sold_price:
            str_list.append('%s销售价格: %s ===>> %s' % (instance.product.sku, instance.__original_sold_price, instance.sold_price))
        if instance.__original_sent_qty != instance.sent_qty:
            str_list.append('%s新增发货数量: %s' % (instance.product.sku, instance.sent_qty - instance.__original_sent_qty))
        if instance.__original_paid_qty != instance.paid_qty:
            str_list.append('%s新增结算数量: %s' % (instance.product.sku, instance.paid_qty - instance.__original_paid_qty))

        if str_list:
            op = OperateLog()
            if request:
                op.user = request.user
            op.op_log = '; '.join(str_list)
            op.op_type = 'ORDER'
            op.target_id = instance.order.id
            op.save()

    if created:
        op = OperateLog()
        if request:
            op.user = request.user
        op.op_log = '增加了新sku：%s(%s)' % (instance.product.sku, instance.product.p_name)
        op.op_type = 'ORDER'
        op.target_id = instance.order.id
        op.save()


# 记录删除销售单明细产品的操作日志
@receiver(post_delete, sender=OrderDetail)
def order_detail_delete_signal(sender, instance, **kwargs):
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
    op.op_log = '删除sku：%s(%s)' % (instance.product.sku, instance.product.p_name)
    op.op_type = 'ORDER'
    op.target_id = instance.order.id
    op.save()


# 记录新增销售单标签的操作日志
@receiver(post_save, sender=OrderTag)
def order_tag_create_signal(sender, instance, created, **kwargs):
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
        op.op_type = 'ORDER'
        op.target_id = instance.order.id
        op.save()


# 记录删除销售单标签的操作日志
@receiver(post_delete, sender=OrderTag)
def order_tag_delete_signal(sender, instance, **kwargs):
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
    op.op_type = 'ORDER'
    op.target_id = instance.order.id
    op.save()