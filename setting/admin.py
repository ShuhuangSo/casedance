from django.contrib import admin
from .models import Tag, OperateLog, Menu


# Register your models here.


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['type', 'color', 'tag_name', 'user']
    list_filter = ['type', 'color', 'user']
    search_fields = ['tag_name']


@admin.register(OperateLog)
class OperateLogAdmin(admin.ModelAdmin):
    list_display = ['op_type', 'op_log', 'target_id', 'user', 'create_time']
    list_filter = ['op_type', 'target_id', 'user']
    search_fields = ['op_log']


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['id', 'parent', 'path', 'component', 'name', 'icon', 'order_num', 'is_active', 'user']
    list_filter = ['is_active', 'user']
    search_fields = ['name']

