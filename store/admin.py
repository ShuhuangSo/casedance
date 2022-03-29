from django.contrib import admin
from .models import Store, Stock, StockInOut, StockInOutDetail


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


@admin.register(StockInOut)
class StockInOutAdmin(admin.ModelAdmin):
    list_display = ['batch_number', 'origin_store', 'target_store', 'user', 'type']
    list_filter = ['type', 'is_active']
    search_fields = ['batch_number', ]


@admin.register(StockInOutDetail)
class StockInOutDetailAdmin(admin.ModelAdmin):
    list_display = ['stock_in_out', 'product', 'qty', 'stock_before']
    list_filter = ['stock_in_out', ]
    search_fields = ['product', ]
