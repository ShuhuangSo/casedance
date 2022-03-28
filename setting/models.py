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
    user = models.ForeignKey(User, related_name='user_tag', on_delete=models.SET_NULL, null=True, verbose_name='user', help_text='user')

    class Meta:
        verbose_name = '标签库'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.tag_name
