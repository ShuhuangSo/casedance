from __future__ import absolute_import
from celery import shared_task
from datetime import datetime

from bonus.models import MonthList
from setting.models import TaskLog


@shared_task
# 生成当月月份
def create_month():
    d = datetime.now().strftime("%Y%m")
    is_exist = MonthList.objects.filter(month=d).count()
    if not is_exist:
        ml = MonthList()
        ml.month = d
        ml.save()

    # 记录执行日志
    task_log = TaskLog()
    task_log.task_type = 8
    task_log.note = '生成当月月份'
    task_log.save()
    return 'OK'