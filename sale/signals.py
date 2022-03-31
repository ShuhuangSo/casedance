import time
from random import Random
import inspect

from django.db.models.signals import pre_save, post_save, post_init, post_delete
from django.dispatch import receiver

from sale.models import Customer, CustomerDiscount, CustomerTag
from setting.models import OperateLog


# 客户创建前生成客户代码并保存
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
