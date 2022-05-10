from __future__ import absolute_import
from celery import shared_task


@shared_task
# 定义的定时任务函数
def auto_sc():
    print('测试任务～～～')
    return 'halo'
