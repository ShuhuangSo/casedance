import time
from random import Random

from django.db.models.signals import pre_save, post_save, post_init, post_delete
from django.dispatch import receiver

from sale.models import Customer


# 客户创建前生成客户代码并保存
@receiver(pre_save, sender=Customer)
def customer_code_signal(sender, instance, created=False, **kwargs):
    if instance._state.adding:  #  判断是否create
        # 获取不重复的客户代码
        if Customer.objects.all().count():
            cus_id = Customer.objects.first().id
        else:
            cus_id = 1
        random_ins = Random()
        code = 'C{time_str}{ranstr}{cus_id}'.format(time_str=time.strftime('%Y%m'),
                                                    ranstr=random_ins.randint(10, 99), cus_id=cus_id)
        instance.customer_code = code
