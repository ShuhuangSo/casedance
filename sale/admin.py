from django.contrib import admin

# Register your models here.
from sale.models import Customer, CustomerDiscount, CustomerTag


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'customer_code', 'pay_way', 'contact_name', 'is_active']
    list_filter = ['is_active', 'pay_way']
    search_fields = ['company_name', ]


@admin.register(CustomerDiscount)
class CustomerDiscountAdmin(admin.ModelAdmin):
    list_display = ['customer', 'p_series', 'discount_type', 'discount_money', 'discount_percent']
    list_filter = ['discount_type', 'p_series']
    search_fields = ['customer', ]


@admin.register(CustomerTag)
class CustomerTagAdmin(admin.ModelAdmin):
    list_display = ['customer', 'tag']
