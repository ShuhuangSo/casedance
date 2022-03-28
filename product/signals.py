from django.db.models.signals import post_save, post_init
from django.dispatch import receiver

from product.models import Product
from setting.models import OperateLog
from store.models import Store, Stock


# 数据保存后，如果不是新建数据，将新旧数据拿出来对比
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


# 数据保存前的初始化，将原数据保存起来
@receiver(post_init, sender=Product)
def product_init_signal(instance, **kwargs):
    instance.__original_p_name = instance.p_name
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
