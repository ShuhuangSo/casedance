from django.db.models.signals import post_save, post_init
from django.dispatch import receiver

from product.models import Product
from setting.models import OperateLog
from store.models import Store, Stock


# 产品数据保存后，如果不是新建数据，将新旧数据拿出来对比
@receiver(post_save, sender=Product)
def product_edit_signal(sender, instance, created, **kwargs):
    # 获取当前user
    import inspect
    for frame_record in inspect.stack():
        if frame_record[3] == 'get_response':
            request = frame_record[0].f_locals['request']
            break
    else:
        request = None
    print(request.user)

    if not created:
        # 记录修改操作日志
        str_list = []
        if instance.__original_p_name != instance.p_name:
            str_list.append('名称: %s ===>> %s' % (instance.__original_p_name, instance.p_name))
        if instance.__original_sku != instance.sku:
            str_list.append('sku: %s ===>> %s' % (instance.__original_sku, instance.sku))
        if instance.__original_status != instance.status:
            str_list.append('状态: %s ===>> %s' % (instance.__original_status, instance.status))
        if instance.__original_brand != instance.brand:
            str_list.append('品牌: %s ===>> %s' % (instance.__original_brand, instance.brand))
        if instance.__original_series != instance.series:
            str_list.append('产品系列: %s ===>> %s' % (instance.__original_series, instance.series))
        if instance.__original_p_type != instance.p_type:
            str_list.append('产品类型: %s ===>> %s' % (instance.__original_p_type, instance.p_type))
        if instance.__original_unit_cost != instance.unit_cost:
            str_list.append('成本价: %s ===>> %s' % (instance.__original_unit_cost, instance.unit_cost))
        if instance.__original_sale_price != instance.sale_price:
            str_list.append('销售定价: %s ===>> %s' % (instance.__original_sale_price, instance.sale_price))
        if instance.__original_length != instance.length:
            str_list.append('长: %s ===>> %s' % (instance.__original_length, instance.length))
        if instance.__original_width != instance.width:
            str_list.append('宽: %s ===>> %s' % (instance.__original_width, instance.width))
        if instance.__original_heigth != instance.heigth:
            str_list.append('高: %s ===>> %s' % (instance.__original_heigth, instance.heigth))
        if instance.__original_weight != instance.weight:
            str_list.append('重量: %s ===>> %s' % (instance.__original_weight, instance.weight))
        if instance.__original_url != instance.url:
            str_list.append('url: %s ===>> %s' % (instance.__original_url, instance.url))
        if instance.__original_is_auto_promote != instance.is_auto_promote:
            str_list.append('补货推荐: %s ===>> %s' % (instance.__original_is_auto_promote, instance.is_auto_promote))
        if instance.__original_stock_strategy != instance.stock_strategy:
            str_list.append('备货策略: %s ===>> %s' % (instance.__original_stock_strategy, instance.stock_strategy))
        if instance.__original_stock_days != instance.stock_days:
            str_list.append('备货天数: %s ===>> %s' % (instance.__original_stock_days, instance.stock_days))
        if instance.__original_alert_qty != instance.alert_qty:
            str_list.append('警戒库存: %s ===>> %s' % (instance.__original_alert_qty, instance.alert_qty))
        if instance.__original_alert_days != instance.alert_days:
            str_list.append('警戒天数: %s ===>> %s' % (instance.__original_alert_days, instance.alert_days))
        if instance.__original_mini_pq != instance.mini_pq:
            str_list.append('最小采购量: %s ===>> %s' % (instance.__original_mini_pq, instance.mini_pq))
        if instance.__original_max_pq != instance.max_pq:
            str_list.append('采购上限: %s ===>> %s' % (instance.__original_max_pq, instance.max_pq))
        if instance.__original_note != instance.note:
            str_list.append('备注: %s ===>> %s' % (instance.__original_note, instance.note))

        op = OperateLog()
        if request:
            op.user = request.user
        op.op_log = ';'.join(str_list)
        op.op_type = 'PRODUCT'
        op.target_id = instance.id
        op.save()

    if created:
        # 如果是新建产品，则为所有门店创建一份产品库存记录
        queryset = Store.objects.all()
        if queryset:
            add_list = []
            for store in queryset:
                add_list.append(Stock(product=instance, store=store))
                print(add_list)
            Stock.objects.bulk_create(add_list)

        #  记录创建产品日志
        op = OperateLog()
        if request:
            op.user = request.user
        op.op_log = '创建了产品'
        op.op_type = 'PRODUCT'
        op.target_id = instance.id
        op.save()


# 产品数据保存前的初始化，将原数据保存起来
@receiver(post_init, sender=Product)
def product_init_signal(instance, **kwargs):
    instance.__original_p_name = instance.p_name
    instance.__original_sku = instance.sku
    instance.__original_status = instance.status
    instance.__original_brand = instance.brand
    instance.__original_series = instance.series
    instance.__original_p_type = instance.p_type
    instance.__original_unit_cost = instance.unit_cost
    instance.__original_sale_price = instance.sale_price
    instance.__original_length = instance.length
    instance.__original_width = instance.width
    instance.__original_heigth = instance.heigth
    instance.__original_weight = instance.weight
    instance.__original_url = instance.url
    instance.__original_is_auto_promote = instance.is_auto_promote
    instance.__original_stock_strategy = instance.stock_strategy
    instance.__original_stock_days = instance.stock_days
    instance.__original_alert_qty = instance.alert_qty
    instance.__original_alert_days = instance.alert_days
    instance.__original_mini_pq = instance.mini_pq
    instance.__original_max_pq = instance.max_pq
    instance.__original_note = instance.note
