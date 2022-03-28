from django.contrib import admin
from .models import Store, Stock


# Register your models here.


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['supplier_name']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['qty', 'lock_qty', 'product', 'store', 'lock_qty']
    list_filter = ['product', 'store', 'is_active']
    search_fields = ['product', 'store']