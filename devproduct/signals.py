from django.db.models.signals import post_save, post_init, post_delete
from django.dispatch import receiver
import inspect

from mercado.models import MLOperateLog
from devproduct.models import DevProduct


# 产品数据保存后，如果不是新建数据，将新旧数据拿出来对比
@receiver(post_save, sender=DevProduct)
def product_edit_signal(sender, instance, created, **kwargs):
    # 获取当前user
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None

    if not created:
        # 记录修改操作日志
        if instance.__original_sku != instance.sku:
            value = 'SKU: %s ===>> %s' % (instance.__original_sku,
                                          instance.sku)
            create_log(instance.id, value, request.user)
        if instance.__original_cn_name != instance.cn_name:
            value = '中文名称: %s ===>> %s' % (instance.__original_cn_name,
                                           instance.cn_name)
            create_log(instance.id, value, request.user)
        if instance.__original_en_name != instance.en_name:
            value = '英文名称: %s ===>> %s' % (instance.__original_en_name,
                                           instance.en_name)
            create_log(instance.id, value, request.user)
        if instance.__original_is_elec != instance.is_elec:
            value = '是否带电: %s ===>> %s' % (instance.__original_is_elec,
                                           instance.is_elec)
            create_log(instance.id, value, request.user)
        if instance.__original_is_magnet != instance.is_magnet:
            value = '是否带磁: %s ===>> %s' % (instance.__original_is_magnet,
                                           instance.is_magnet)
            create_log(instance.id, value, request.user)
        if instance.__original_is_water != instance.is_water:
            value = '是否带液体: %s ===>> %s' % (instance.__original_is_water,
                                            instance.is_water)
            create_log(instance.id, value, request.user)
        if instance.__original_is_dust != instance.is_dust:
            value = '是否粉末: %s ===>> %s' % (instance.__original_is_dust,
                                           instance.is_dust)
            create_log(instance.id, value, request.user)
        if instance.__original_keywords != instance.keywords:
            value = '搜索关键词: %s ===>> %s' % (instance.__original_keywords,
                                            instance.keywords)
            create_log(instance.id, value, request.user)
        if instance.__original_p_weight != instance.p_weight:
            value = '重量g: %s ===>> %s' % (instance.__original_p_weight,
                                          instance.p_weight)
            create_log(instance.id, value, request.user)
        if instance.__original_p_length != instance.p_length:
            value = '长cm: %s ===>> %s' % (instance.__original_p_length,
                                          instance.p_length)
            create_log(instance.id, value, request.user)
        if instance.__original_p_width != instance.p_width:
            value = '宽cm: %s ===>> %s' % (instance.__original_p_width,
                                          instance.p_width)
            create_log(instance.id, value, request.user)
        if instance.__original_p_height != instance.p_height:
            value = '高cm: %s ===>> %s' % (instance.__original_p_height,
                                          instance.p_height)
            create_log(instance.id, value, request.user)
        if instance.__original_is_confirm_data != instance.is_confirm_data:
            value = '确认重量尺寸: %s ===>> %s' % (
                instance.__original_is_confirm_data, instance.is_confirm_data)
            create_log(instance.id, value, request.user)
        if instance.__original_unit_cost != instance.unit_cost:
            value = '成本价: %s ===>> %s' % (instance.__original_unit_cost,
                                          instance.unit_cost)
            create_log(instance.id, value, request.user)
        if instance.__original_package_included != instance.package_included:
            value = '产品清单列表: %s ===>> %s' % (
                instance.__original_package_included,
                instance.package_included)
            create_log(instance.id, value, request.user)
        if instance.__original_desc != instance.desc:
            value = '修改了产品描述'
            create_log(instance.id, value, request.user)
        if instance.__original_note != instance.note:
            value = '修改了备注'
            create_log(instance.id, value, request.user)
        if instance.__original_category != instance.category:
            value = '修改了类目'
            create_log(instance.id, value, request.user)
        if instance.__original_buy_url1 != instance.buy_url1:
            value = '修改了产品采购链接1'
            create_log(instance.id, value, request.user)
        if instance.__original_buy_url2 != instance.buy_url2:
            value = '修改了产品采购链接2'
            create_log(instance.id, value, request.user)
        if instance.__original_buy_url3 != instance.buy_url3:
            value = '修改了产品采购链接3'
            create_log(instance.id, value, request.user)
        if instance.__original_buy_url4 != instance.buy_url4:
            value = '修改了产品采购链接4'
            create_log(instance.id, value, request.user)
        if instance.__original_buy_url5 != instance.buy_url5:
            value = '修改了产品采购链接5'
            create_log(instance.id, value, request.user)
        if instance.__original_refer_url1 != instance.refer_url1:
            value = '修改了参考链接1'
            create_log(instance.id, value, request.user)
        if instance.__original_refer_url2 != instance.refer_url2:
            value = '修改了参考链接2'
            create_log(instance.id, value, request.user)
        if instance.__original_tag_name != instance.tag_name:
            value = '修改了标签名称'
            create_log(instance.id, value, request.user)
        if instance.__original_rate != instance.rate:
            value = '产品打分: %s星 ===>> %s星' % (instance.__original_rate,
                                             instance.rate)
            create_log(instance.id, value, request.user)


# 产品数据保存前的初始化，将原数据保存起来
@receiver(post_init, sender=DevProduct)
def product_init_signal(instance, **kwargs):
    instance.__original_sku = instance.sku
    instance.__original_cn_name = instance.cn_name
    instance.__original_en_name = instance.en_name
    instance.__original_is_elec = instance.is_elec
    instance.__original_is_magnet = instance.is_magnet
    instance.__original_is_water = instance.is_water
    instance.__original_is_dust = instance.is_dust
    instance.__original_keywords = instance.keywords
    instance.__original_p_weight = instance.p_weight
    instance.__original_p_length = instance.p_length
    instance.__original_p_width = instance.p_width
    instance.__original_p_height = instance.p_height
    instance.__original_is_confirm_data = instance.is_confirm_data
    instance.__original_unit_cost = instance.unit_cost
    instance.__original_package_included = instance.package_included
    instance.__original_desc = instance.desc
    instance.__original_category = instance.category
    instance.__original_note = instance.note
    instance.__original_buy_url1 = instance.buy_url1
    instance.__original_buy_url2 = instance.buy_url2
    instance.__original_buy_url3 = instance.buy_url3
    instance.__original_buy_url4 = instance.buy_url4
    instance.__original_buy_url5 = instance.buy_url5
    instance.__original_refer_url1 = instance.refer_url1
    instance.__original_refer_url2 = instance.refer_url2
    instance.__original_rate = instance.rate
    instance.__original_tag_name = instance.tag_name


def create_log(pid, value, user):
    # 创建操作日志
    log = MLOperateLog()
    log.op_module = 'DEVP'
    log.op_type = 'EDIT'
    log.target_type = 'DEVP_P'
    log.target_id = pid
    log.desc = '修改产品 {name}'.format(name=value)
    log.user = user
    log.save()
