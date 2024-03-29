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
        ('PURCHASE', '采购标签'),
        ('CUSTOMER', '客户标签'),
    )

    type = models.CharField(max_length=10, choices=TAG_TYPE, default='PRODUCT', verbose_name='标签类型',
                            help_text='标签类型')
    color = models.CharField(max_length=10, verbose_name='标签颜色', help_text='标签颜色')
    tag_name = models.CharField(max_length=30, verbose_name='标签名称', help_text='标签名称')
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
    user = models.ForeignKey(User, related_name='user_op_log', on_delete=models.DO_NOTHING, null=True,
                             verbose_name='user',
                             help_text='user')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='操作时间', help_text='操作时间')

    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.op_type


class Menu(models.Model):
    """
    前端导航菜单
    """
    parent = models.ForeignKey("Menu", on_delete=models.DO_NOTHING, null=True, blank=True,
                               related_name='children', verbose_name='父id', help_text='父id')
    path = models.CharField(max_length=100, null=True, blank=True, verbose_name='路由地址', help_text='路由地址')
    component = models.CharField(max_length=30, null=True, blank=True, verbose_name='组件', help_text='组件')
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name='菜单名', help_text='菜单名')
    icon = models.CharField(max_length=30, null=True, blank=True, verbose_name='icon图标', help_text='icon图标')

    order_num = models.IntegerField(default=1, verbose_name='排序号', help_text='排序号')
    is_active = models.BooleanField(default=True, verbose_name='是否启用', help_text='是否启用')
    user = models.ForeignKey(User, related_name='user_menu', on_delete=models.SET_NULL, null=True,
                             verbose_name='user',
                             help_text='user')

    class Meta:
        verbose_name = '前端导航菜单'
        verbose_name_plural = verbose_name
        ordering = ['order_num']

    def __str__(self):
        return str(self.id)


class MLUserPermission(models.Model):
    """
    美客多操作权限
    """
    parent = models.ForeignKey("MLUserPermission", on_delete=models.DO_NOTHING, null=True, blank=True,
                               related_name='children', verbose_name='父id', help_text='父id')
    component = models.CharField(max_length=30, null=True, blank=True, verbose_name='组件名称', help_text='组件名称')
    module_name = models.CharField(max_length=50, null=True, blank=True, verbose_name='模块名称', help_text='模块名称')
    order_num = models.IntegerField(default=1, verbose_name='排序号', help_text='排序号')
    is_active = models.BooleanField(default=True, verbose_name='是否启用', help_text='是否启用')
    user = models.ForeignKey(User, related_name='user_mlPermission', on_delete=models.SET_NULL, null=True,
                             verbose_name='user',
                             help_text='user')

    class Meta:
        verbose_name = '美客多操作权限'
        verbose_name_plural = verbose_name
        ordering = ['order_num']

    def __str__(self):
        return str(self.id)


class TaskLog(models.Model):
    """
    任务执行日志
    task_type:
    1：采购推荐 2:  销量计算
    """

    task_type = models.IntegerField(default=0, verbose_name='任务类型', help_text='任务类型')
    note = models.CharField(max_length=20, verbose_name='任务注释', help_text='任务注释')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='执行时间', help_text='执行时间')

    class Meta:
        verbose_name = '任务执行日志'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.note


class SysRefill(models.Model):
    """
    补货推荐设置
    """

    sys_alert_qty = models.IntegerField(default=0, verbose_name='警戒库存', help_text='警戒库存')
    sys_mini_pq = models.IntegerField(default=0, verbose_name='最小采购量', help_text='最小采购量')
    sys_max_pq = models.IntegerField(default=0, verbose_name='采购上限', help_text='采购上限')
    sys_stock_days = models.IntegerField(default=0, verbose_name='备货天数', help_text='备货天数')

    class Meta:
        verbose_name = '补货推荐设置'
        verbose_name_plural = verbose_name
        ordering = ['sys_alert_qty']

    def __str__(self):
        return str(self.id)