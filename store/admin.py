from django.contrib import admin
from .models import Store, Stock, StockInOut, StockInOutDetail, StockLog


# Register your models here.


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['supplier_name']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['id', 'qty', 'lock_qty', 'product', 'store', 'create_time']
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
    search_fields = ['product', ]


@admin.register(StockLog)
class StockLogAdmin(admin.ModelAdmin):
    list_display = ['op_type', 'product', 'qty', 'op_origin_id', 'store', 'user', 'create_time']
    list_filter = ['op_type', ]
    search_fields = ['product', ]
