from django.contrib import admin

from report.models import SalesReport, StockReport, CustomerReport


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ['qty', 'amount', 'series', 'sale_date']
    list_filter = ['series']


@admin.register(StockReport)
class StockReportAdmin(admin.ModelAdmin):
    list_display = ['qty', 'amount', 'series', 'stock_date']
    list_filter = ['series']


@admin.register(CustomerReport)
class CustomerReportAdmin(admin.ModelAdmin):
    list_display = ['qty', 'amount', 'series', 'calc_date', 'customer']
    list_filter = ['series', 'customer']