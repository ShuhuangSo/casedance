from django.contrib import admin

# Register your models here.
from purchase.models import PurchaseOrder, PurchaseDetail, PurchaseOrderTag, PostInfo


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


@admin.register(PurchaseOrderTag)
class PurchaseOrderTagAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'tag']
    list_filter = ['purchase_order', ]
    search_fields = ['purchase_order', ]


@admin.register(PostInfo)
class PostInfoAdmin(admin.ModelAdmin):
    list_display = ['logistic', 'tracking_number', 'package_count']
    list_filter = ['logistic', ]
    search_fields = ['logistic', ]
