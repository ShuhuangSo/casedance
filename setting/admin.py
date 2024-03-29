from django.contrib import admin
from .models import Tag, OperateLog, Menu, TaskLog, SysRefill, MLUserPermission


# Register your models here.


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['type', 'color', 'tag_name', 'user']
    list_filter = ['type', 'color', 'user']
    search_fields = ['tag_name']


@admin.register(OperateLog)
class OperateLogAdmin(admin.ModelAdmin):
    list_display = ['op_type', 'op_log', 'target_id', 'user', 'create_time']
    list_filter = ['op_type', 'user']
    search_fields = ['op_log']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['id', 'parent', 'path', 'component', 'name', 'icon', 'order_num', 'is_active', 'user']
    list_filter = ['is_active', 'user']
    search_fields = ['name']


@admin.register(MLUserPermission)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['id', 'parent', 'module_name', 'component', 'order_num', 'is_active', 'user']
    list_filter = ['is_active', 'user']
    search_fields = ['name']


@admin.register(TaskLog)
class TaskLogAdmin(admin.ModelAdmin):
    list_display = ['task_type', 'note', 'create_time']
    list_filter = ['task_type']


@admin.register(SysRefill)
class SysRefillAdmin(admin.ModelAdmin):
    list_display = ['sys_alert_qty', 'sys_mini_pq', 'sys_max_pq', 'sys_stock_days']
