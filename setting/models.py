from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class Tag(models.Model):
    """
    标签库
    """
    TAG_TYPE = (
        ('PRODUCT', '产品标签'),
        ('ORDER', '订单标签'),
        ('CUSTOMER', '客户标签'),
    )

    type = models.CharField(max_length=10, choices=TAG_TYPE, default='PRODUCT', verbose_name='标签类型',
                            help_text='标签类型')
    color = models.CharField(max_length=10, verbose_name='标签颜色', help_text='标签颜色')
    tag_name = models.CharField(max_length=30, unique=True, verbose_name='标签名称', help_text='标签名称')
    user = models.ForeignKey(User, related_name='user_tag', on_delete=models.SET_NULL, null=True, verbose_name='user',
                             help_text='user')

    class Meta:
        verbose_name = '标签库'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.tag_name


class OperateLog(models.Model):
    """
    操作日志
    """
    O_TYPE = (
        ('PRODUCT', '产品操作'),
        ('ORDER', '销售单操作'),
        ('CUSTOMER', '客户管理操作'),
        ('PURCHASE', '采购单操作'),
        ('STORE', '店铺资料操作'),
    )

    op_type = models.CharField(max_length=10, choices=O_TYPE, default='PRODUCT', verbose_name='日志类型',
                               help_text='日志类型')
    op_log = models.TextField(null=True, blank=True, default='', verbose_name='操作描述', help_text='操作描述')
    target_id = models.IntegerField(null=True, blank=True, verbose_name='目标id', help_text='目标id')
    user = models.ForeignKey(User, related_name='user_op_log', on_delete=models.DO_NOTHING, null=True, verbose_name='user',
                             help_text='user')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间', help_text='操作时间')

    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.op_type
