from django.contrib import admin
from .models import Store

# Register your models here.


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['supplier_name']