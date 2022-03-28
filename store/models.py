from django.db import models


# Create your models here.


class Store(models.Model):
    """
    仓库、销售门店
    """
    S_TYPE = (
        ('WAREHOUSE', '仓库'),
        ('STORE', '门店'),
    )

    store_name = models.CharField(max_length=80, verbose_name='店铺名称', help_text='店铺名称')
    type = models.CharField(max_length=10, choices=S_TYPE, default='STORE', verbose_name='店铺类型',
                            help_text='店铺类型')
    address = models.CharField(null=True, blank=True, max_length=200, verbose_name='地址', help_text='地址')
    contact_name = models.CharField(null=True, blank=True, max_length=20, verbose_name='联系人', help_text='联系人')
    phone = models.CharField(null=True, blank=True, max_length=15, verbose_name='电话', help_text='电话')
    qq = models.CharField(null=True, blank=True, max_length=15, verbose_name='QQ', help_text='QQ')
    wechat = models.CharField(null=True, blank=True, max_length=15, verbose_name='微信', help_text='微信')
    website = models.CharField(null=True, blank=True, max_length=200, verbose_name='网址', help_text='网址')
    is_active = models.BooleanField(default=True, verbose_name='状态', help_text='状态')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '销售门店'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.store_name
