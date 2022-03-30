from django.contrib import admin

# Register your models here.
from purchase.models import PurchaseOrder, PurchaseDetail


@admin.register(PurchaseOrder)
class StockInOutAdmin(admin.ModelAdmin):
    list_display = ['p_number', 'store', 'supplier', 'user', 'order_status']
    list_filter = ['order_status', 'is_active']
    search_fields = ['p_number', ]


@admin.register(PurchaseDetail)
class StockInOutAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'product', 'qty', 'paid_qty', 'unit_cost', 'is_paid']
    list_filter = ['is_paid', ]
    search_fields = ['product', ]
