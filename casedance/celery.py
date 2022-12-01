from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
from django.conf import settings

# 指定Django默认配置文件模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'casedance.settings')

# 为我们的项目myproject创建一个Celery实例。这里不指定broker backend 容易出现错误。
# 如果没有密码 使用 'redis://127.0.0.1:6379/0'
app = Celery('casedance', broker='redis://127.0.0.1:6379/0', backend='redis://127.0.0.1:6379/0')

# 这里指定从django的settings.py里读取celery配置
app.config_from_object('django.conf:settings')
# 下面的设置就是关于调度器beat的设置,
# 具体参考https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html
app.conf.beat_schedule = {
    'every-one-hour': {  # 取个名字
        'task': 'purchase.tasks.calc_sold_qty',  # 销量计算
        # 'schedule': crontab(), 调用crontab进行具体时间的定义
        'schedule': timedelta(hours=1),
    },
    'every-12-hour': {
        'task': 'purchase.tasks.calc_refill',  # 补货推荐计算
        'schedule': timedelta(hours=12),
    },
    'every-3-days': {
        'task': 'product.tasks.check_new_models',  # 获取最近更新的手机型号
        'schedule': timedelta(days=3),
    },
    'update_spec': {
        'task': 'product.tasks.update_spec',  # 获取手机型号参数
        'schedule': timedelta(days=5),
    },
    'calc_total_sales': {
        'task': 'report.tasks.calc_total_sale',  # 总销量计算
        'schedule': crontab(hour='0', minute='1'),  # 每天0点1分开始计算
    },
    'calc_customer_sales': {
        'task': 'report.tasks.calc_customer_report',  # 计算所有客户60天的销量数据
        'schedule': crontab(hour='0', minute='10'),  # 每天0点10分开始计算
    },
    'calc_product_sales': {
        'task': 'report.tasks.calc_product_sale',  # 计算sku产品60天每天销量
        'schedule': crontab(hour='0', minute='30'),  # 每天0点30分开始计算
    },
    'create_month': {
        'task': 'bonus.tasks.create_month',  # 生成当月月份
        'schedule': crontab(minute=0, hour=1, day_of_month=1),  # 每月1号执行
    },
    'track_listing': {
        'task': 'mercado.tasks.track_listing',  # 每天更新链接信息并进行销量计算
        'schedule': crontab(hour='0', minute='3'),  # 每天0点1分开始计算
    },
    'track_seller': {
        'task': 'mercado.tasks.track_seller',  # 每天更新卖家信息并进行销量计算
        'schedule': crontab(hour='0', minute='30'),  # 每天0点30分开始计算
    },
    'delete_logs': {
        'task': 'product.tasks.delete_logs',  # 删除1个月前任务执行日志
        'schedule': crontab(minute=0, hour=2, day_of_month=1),  # 每月1号执行
    },
    'fbm_product_sales': {
        'task': 'mercado.tasks.calc_product_sales',  # 每天更新fbm产品销量信息计算
        'schedule': crontab(hour='0', minute='40'),  # 每天0点40分开始计算
    },
}
# 自动从所有已注册的django app中加载任务
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)