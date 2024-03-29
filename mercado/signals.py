from django.db.models.signals import post_save, post_init, post_delete
from django.dispatch import receiver
import inspect

from mercado.models import MLProduct, MLOperateLog, Packing, Ship, ShipDetail, PurchaseManage


# 产品数据保存后，如果不是新建数据，将新旧数据拿出来对比
@receiver(post_save, sender=MLProduct)
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
        if instance.__original_p_name != instance.p_name:
            value = '名称: %s ===>> %s' % (instance.__original_p_name, instance.p_name)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'p_name', instance.p_name, request.user)  # 更新未发货运单的产品参数
            update_purchase_product(instance.sku, 'p_name', instance.p_name)  # 更新采购管理的产品参数
        if instance.__original_platform != instance.platform:
            value = '平台: %s ===>> %s' % (instance.__original_platform, instance.platform)
            create_log(instance.id, value, request.user)
        if instance.__original_label_code != instance.label_code:
            value = 'FBM条码: %s ===>> %s' % (instance.__original_label_code, instance.label_code)
            create_log(instance.id, value, request.user)
        if instance.__original_upc != instance.upc:
            value = 'UPC: %s ===>> %s' % (instance.__original_upc, instance.upc)
            create_log(instance.id, value, request.user)
        if instance.__original_item_id != instance.item_id:
            value = 'ItemID: %s ===>> %s' % (instance.__original_item_id, instance.item_id)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'item_id', instance.item_id, request.user)  # 更新未发货运单的产品参数
        if instance.__original_custom_code != instance.custom_code:
            value = '海关编码: %s ===>> %s' % (instance.__original_custom_code, instance.custom_code)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'custom_code', instance.custom_code, request.user)  # 更新未发货运单的产品参数
        if instance.__original_cn_name != instance.cn_name:
            value = '中文品名: %s ===>> %s' % (instance.__original_cn_name, instance.cn_name)
            create_log(instance.id, value, request.user)
        if instance.__original_en_name != instance.en_name:
            value = '英文品名: %s ===>> %s' % (instance.__original_en_name, instance.en_name)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'en_name', instance.en_name, request.user)  # 更新未发货运单的产品参数
        if instance.__original_brand != instance.brand:
            value = '品牌: %s ===>> %s' % (instance.__original_brand, instance.brand)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'brand', instance.brand, request.user)  # 更新未发货运单的产品参数
        if instance.__original_declared_value != instance.declared_value:
            value = '申报价值: %s ===>> %s' % (instance.__original_declared_value, instance.declared_value)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'declared_value', instance.declared_value, request.user)  # 更新未发货运单的产品参数
        if instance.__original_cn_material != instance.cn_material:
            value = '中文材质: %s ===>> %s' % (instance.__original_cn_material, instance.cn_material)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'cn_material', instance.cn_material, request.user)  # 更新未发货运单的产品参数
        if instance.__original_en_material != instance.en_material:
            value = '英文材质: %s ===>> %s' % (instance.__original_en_material, instance.en_material)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'en_material', instance.en_material, request.user)  # 更新未发货运单的产品参数
        if instance.__original_use != instance.use:
            value = '用途: %s ===>> %s' % (instance.__original_use, instance.use)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'use', instance.use, request.user)  # 更新未发货运单的产品参数
        if instance.__original_is_elec != instance.is_elec:
            value = '是否带电: %s ===>> %s' % (instance.__original_is_elec, instance.is_elec)
            create_log(instance.id, value, request.user)
        if instance.__original_is_magnet != instance.is_magnet:
            value = '是否带磁: %s ===>> %s' % (instance.__original_is_magnet, instance.is_magnet)
            create_log(instance.id, value, request.user)
        if instance.__original_is_water != instance.is_water:
            value = '是否液体: %s ===>> %s' % (instance.__original_is_water, instance.is_water)
            create_log(instance.id, value, request.user)
        if instance.__original_p_status != instance.p_status:
            value = '状态: %s ===>> %s' % (instance.__original_p_status, instance.p_status)
            create_log(instance.id, value, request.user)
        if instance.__original_site != instance.site:
            value = '站点: %s ===>> %s' % (instance.__original_site, instance.site)
            create_log(instance.id, value, request.user)
        if instance.__original_shop != instance.shop:
            value = '上架店铺: %s ===>> %s' % (instance.__original_shop, instance.shop)
            create_log(instance.id, value, request.user)
        if instance.__original_weight != instance.weight:
            value = '重量: %s ===>> %s' % (instance.__original_weight, instance.weight)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'weight', instance.weight, request.user)  # 更新未发货运单的产品参数
        if instance.__original_length != instance.length:
            value = '长: %s ===>> %s' % (instance.__original_length, instance.length)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'length', instance.length, request.user)  # 更新未发货运单的产品参数
        if instance.__original_width != instance.width:
            value = '宽: %s ===>> %s' % (instance.__original_width, instance.width)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'width', instance.width, request.user)  # 更新未发货运单的产品参数
        if instance.__original_heigth != instance.heigth:
            value = '高: %s ===>> %s' % (instance.__original_heigth, instance.heigth)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'heigth', instance.heigth, request.user)  # 更新未发货运单的产品参数
        if instance.__original_unit_cost != instance.unit_cost:
            value = '成本价: %s ===>> %s' % (instance.__original_unit_cost, instance.unit_cost)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'unit_cost', instance.unit_cost, request.user)  # 更新未发货运单的产品参数
            update_purchase_product(instance.sku, 'unit_cost', instance.unit_cost)  # 更新采购管理的产品参数
        if instance.__original_first_ship_cost != instance.first_ship_cost:
            value = '预估头程运费: %s ===>> %s' % (instance.__original_first_ship_cost, instance.first_ship_cost)
            create_log(instance.id, value, request.user)
        if instance.__original_buy_url != instance.buy_url:
            value = '修改了采购链接1'
            create_log(instance.id, value, request.user)
        if instance.__original_buy_url2 != instance.buy_url2:
            value = '修改了采购链接2'
            create_log(instance.id, value, request.user)
        if instance.__original_buy_url3 != instance.buy_url3:
            value = '修改了采购链接3'
            create_log(instance.id, value, request.user)
        if instance.__original_buy_url4 != instance.buy_url4:
            value = '修改了采购链接4'
            create_log(instance.id, value, request.user)
        if instance.__original_buy_url5 != instance.buy_url5:
            value = '修改了采购链接5'
            create_log(instance.id, value, request.user)
        if instance.__original_sale_url != instance.sale_url:
            value = '修改了销售链接'
            create_log(instance.id, value, request.user)
        if instance.__original_refer_url != instance.refer_url:
            value = '修改了参考链接'
            create_log(instance.id, value, request.user)
        if instance.__original_note != instance.note:
            value = '修改了备注'
            create_log(instance.id, value, request.user)
        if instance.__original_packing_id != instance.packing_id:
            old_packing = Packing.objects.filter(id=instance.__original_packing_id).first()
            old_name = old_packing.name if old_packing else '空'
            new_packing = Packing.objects.filter(id=instance.packing_id).first()
            new_name = new_packing.name if new_packing else '空'
            value = '包材: %s ===>> %s' % (old_name, new_name)
            create_log(instance.id, value, request.user)
            update_ship_product(instance.sku, 'packing', instance.packing_id, request.user)  # 更新未发货运单的产品参数
            update_purchase_product(instance.sku, 'packing', instance.packing_id)  # 更新采购管理的产品参数
        if instance.__original_is_checked != instance.is_checked:
            value = '是否核对: %s ===>> %s' % (instance.__original_is_checked, instance.is_checked)
            create_log(instance.id, value, request.user)
        if instance.__original_label_title != instance.label_title:
            value = '链接标题: %s ===>> %s' % (instance.__original_label_title, instance.label_title)
            create_log(instance.id, value, request.user)
        if instance.__original_label_option != instance.label_option:
            value = '链接选项: %s ===>> %s' % (instance.__original_label_option, instance.label_option)
            create_log(instance.id, value, request.user)


# 产品数据保存前的初始化，将原数据保存起来
@receiver(post_init, sender=MLProduct)
def product_init_signal(instance, **kwargs):
    instance.__original_p_name = instance.p_name
    instance.__original_label_code = instance.label_code
    instance.__original_upc = instance.upc
    instance.__original_item_id = instance.item_id
    instance.__original_custom_code = instance.custom_code
    instance.__original_cn_name = instance.cn_name
    instance.__original_en_name = instance.en_name
    instance.__original_brand = instance.brand
    instance.__original_declared_value = instance.declared_value
    instance.__original_cn_material = instance.cn_material
    instance.__original_en_material = instance.en_material
    instance.__original_use = instance.use
    instance.__original_is_elec = instance.is_elec
    instance.__original_is_magnet = instance.is_magnet
    instance.__original_is_water = instance.is_water
    instance.__original_p_status = instance.p_status
    instance.__original_site = instance.site
    instance.__original_shop = instance.shop
    instance.__original_weight = instance.weight
    instance.__original_length = instance.length
    instance.__original_width = instance.width
    instance.__original_heigth = instance.heigth
    instance.__original_unit_cost = instance.unit_cost
    instance.__original_first_ship_cost = instance.first_ship_cost
    instance.__original_buy_url = instance.buy_url
    instance.__original_sale_url = instance.sale_url
    instance.__original_refer_url = instance.refer_url
    instance.__original_note = instance.note
    instance.__original_packing_id = instance.packing_id
    instance.__original_buy_url2 = instance.buy_url2
    instance.__original_buy_url3 = instance.buy_url3
    instance.__original_buy_url4 = instance.buy_url4
    instance.__original_buy_url5 = instance.buy_url5
    instance.__original_is_checked = instance.is_checked
    instance.__original_label_title = instance.label_title
    instance.__original_label_option = instance.label_option
    instance.__original_platform = instance.platform


def create_log(pid, value, user):
    # 创建操作日志
    log = MLOperateLog()
    log.op_module = 'PRODUCT'
    log.op_type = 'EDIT'
    log.target_type = 'PRODUCT'
    log.target_id = pid
    log.desc = '修改产品 {name}'.format(name=value)
    log.user = user
    log.save()


# 更新未发货运单的产品参数
def update_ship_product(sku, field, value, user):
    queryset = ShipDetail.objects.filter(ship__s_status='PREPARING', sku=sku)
    for i in queryset:
        if field == 'p_name':
            i.p_name = value
            i.save()
            log_value = '同步更新%s的产品名称' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'item_id':
            i.item_id = value
            i.save()
            log_value = '同步更新%s的ItemID' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'weight':
            i.weight = value
            i.save()
            log_value = '同步更新%s的重量' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'unit_cost':
            i.unit_cost = value
            i.save()
            log_value = '同步更新%s的成本价' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'length':
            i.length = value
            i.save()
            log_value = '同步更新%s的长cm' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'width':
            i.width = value
            i.save()
            log_value = '同步更新%s的宽cm' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'heigth':
            i.heigth = value
            i.save()
            log_value = '同步更新%s的高cm' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'custom_code':
            i.custom_code = value
            i.save()
            log_value = '同步更新%s的海关编码' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'en_name':
            i.en_name = value
            i.save()
            log_value = '同步更新%s的英文品名' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'brand':
            i.brand = value
            i.save()
            log_value = '同步更新%s的品牌' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'declared_value':
            i.declared_value = value
            i.save()
            log_value = '同步更新%s的申报价值' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'cn_material':
            i.cn_material = value
            i.save()
            log_value = '同步更新%s的中文材质' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'en_material':
            i.en_material = value
            i.save()
            log_value = '同步更新%s的英文材质' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'use':
            i.use = value
            i.save()
            log_value = '同步更新%s的用途' % sku
            create_ship_log(i.ship.id, log_value, user)
            continue
        if field == 'packing':
            p = Packing.objects.filter(id=value).first()
            i.packing_name = p.name
            i.packing_size = p.size
            i.save()
            log_value = '同步更新%s的包材' % sku
            create_ship_log(i.ship.id, log_value, user)


# 更新采购管理的产品参数
def update_purchase_product(sku, field, value):
    queryset = PurchaseManage.objects.filter(sku=sku).exclude(p_status='USED')  # 不包含已出库的产品
    for i in queryset:
        if field == 'p_name':
            i.p_name = value
            i.save()
            continue
        if field == 'unit_cost':
            i.unit_cost = value
            i.save()
            continue
        if field == 'packing':
            p = Packing.objects.filter(id=value).first()
            i.packing_name = p.name
            i.packing_size = p.size
            i.save()


def create_ship_log(pid, value, user):
    # 创建操作日志
    log = MLOperateLog()
    log.op_module = 'SHIP'
    log.op_type = 'EDIT'
    log.target_type = 'SHIP'
    log.target_id = pid
    log.desc = '修改运单 {name}'.format(name=value)
    log.user = user
    log.save()


# 运单数据保存后，如果不是新建数据，将新旧数据拿出来对比
@receiver(post_save, sender=Ship)
def ship_edit_signal(sender, instance, created, **kwargs):
    # 获取当前user
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None

    if not created:
        # 记录修改操作日志
        if instance.__original_s_number != instance.s_number:
            value = '物流商单号: %s ===>> %s' % (instance.__original_s_number, instance.s_number)
            create_ship_log(instance.id, value, request.user)
        if instance.__original_batch != instance.batch:
            value = '批次号: %s ===>> %s' % (instance.__original_batch, instance.batch)
            create_ship_log(instance.id, value, request.user)
        if instance.__original_shop != instance.shop:
            value = '目标店铺: %s ===>> %s' % (instance.__original_shop, instance.shop)
            create_ship_log(instance.id, value, request.user)
        if instance.__original_target != instance.target:
            value = '类型: %s ===>> %s' % (instance.__original_target, instance.target)
            create_ship_log(instance.id, value, request.user)
        if instance.__original_fbm_warehouse != instance.fbm_warehouse:
            value = 'fbm仓库: %s ===>> %s' % (instance.__original_fbm_warehouse, instance.fbm_warehouse)
            create_ship_log(instance.id, value, request.user)
        if instance.__original_envio_number != instance.envio_number:
            value = 'Envio号: %s ===>> %s' % (instance.__original_envio_number, instance.envio_number)
            create_ship_log(instance.id, value, request.user)
        if instance.__original_ship_type != instance.ship_type:
            value = '发货方式: %s ===>> %s' % (instance.__original_ship_type, instance.ship_type)
            create_ship_log(instance.id, value, request.user)
        if instance.__original_carrier != instance.carrier:
            value = '承运商: %s ===>> %s' % (instance.__original_carrier, instance.carrier)
            create_ship_log(instance.id, value, request.user)
        if instance.__original_end_date != str(instance.end_date):
            value = '截单日期: %s ===>> %s' % (instance.__original_end_date, instance.end_date)
            create_ship_log(instance.id, value, request.user)
        if instance.__original_ship_date != str(instance.ship_date):
            value = '航班日期: %s ===>> %s' % (instance.__original_ship_date, instance.ship_date)
            create_ship_log(instance.id, value, request.user)
        if instance.__original_book_date != str(instance.book_date):
            value = 'FBM预约日期: %s ===>> %s' % (instance.__original_book_date, instance.book_date)
            create_ship_log(instance.id, value, request.user)
        if instance.__original_note != instance.note:
            value = '修改备注'
            create_ship_log(instance.id, value, request.user)
        if instance.__original_tag_name != instance.tag_name:
            value = '编辑标签: %s ===>> %s' % (instance.__original_tag_name, instance.tag_name)
            create_ship_log(instance.id, value, request.user)


# 运单数据保存前的初始化，将原数据保存起来
@receiver(post_init, sender=Ship)
def ship_init_signal(instance, **kwargs):
    instance.__original_s_number = instance.s_number
    instance.__original_batch = instance.batch
    instance.__original_shop = instance.shop
    instance.__original_target = instance.target
    instance.__original_fbm_warehouse = instance.fbm_warehouse
    instance.__original_envio_number = instance.envio_number
    instance.__original_ship_type = instance.ship_type
    instance.__original_carrier = instance.carrier
    instance.__original_end_date = str(instance.end_date)
    instance.__original_ship_date = str(instance.ship_date)
    instance.__original_book_date = str(instance.book_date)
    instance.__original_note = instance.note
    instance.__original_tag_name = instance.tag_name


# 运单产品数据保存后，如果不是新建数据，将新旧数据拿出来对比
@receiver(post_save, sender=ShipDetail)
def ship_detail_edit_signal(sender, instance, created, **kwargs):
    # 获取当前user
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None

    if not created:
        # 记录修改操作日志
        if instance.__original_qty != instance.qty:
            value = '%s %s 数量: %s ===>> %s' % (instance.sku, instance.p_name, instance.__original_qty, instance.qty)
            create_ship_log(instance.ship.id, value, request.user)
        if instance.__original_note != instance.note:
            value = '%s %s 备注: %s ===>> %s' % (instance.sku, instance.p_name, instance.__original_note, instance.note)
            create_ship_log(instance.ship.id, value, request.user)
        if instance.__original_s_type != instance.s_type:
            value = '%s %s 货品类型: %s ===>> %s' % (instance.sku, instance.p_name, instance.__original_s_type, instance.s_type)
            create_ship_log(instance.ship.id, value, request.user)


# 运单数据保存前的初始化，将原数据保存起来
@receiver(post_init, sender=ShipDetail)
def ship_detail_init_signal(instance, **kwargs):
    instance.__original_qty = instance.qty
    instance.__original_note = instance.note
    instance.__original_s_type = instance.s_type