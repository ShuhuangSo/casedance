"""
飞书集成 Models
- FeishuUserBinding: 飞书 open_id 与系统用户的绑定关系
"""
from django.db import models
from django.conf import settings


class FeishuUserBinding(models.Model):
    """飞书用户与系统用户的绑定"""
    open_id = models.CharField(
        max_length=64, unique=True,
        verbose_name='飞书 Open ID', help_text='飞书用户唯一标识')
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='feishu_binding',
        verbose_name='系统用户', help_text='关联的系统用户')
    mobile = models.CharField(
        max_length=20, blank=True, default='',
        verbose_name='手机号', help_text='飞书返回的手机号')
    create_time = models.DateTimeField(
        auto_now_add=True, verbose_name='绑定时间', help_text='绑定时间')

    class Meta:
        verbose_name = '飞书用户绑定'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return f'{self.open_id} → {self.user.username}'
