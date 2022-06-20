from django.contrib import admin

from bonus.models import ExchangeRate, BasicInfo, Manager, AccountSales, AccountBonus, Accounts, MonthList


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['currency', 'rate', 'month']
    list_filter = ['currency']
    search_fields = ['currency']


@admin.register(BasicInfo)
class BasicInfoAdmin(admin.ModelAdmin):
    list_display = ['type', 'name']
    list_filter = ['type']
    search_fields = ['name']


@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_leader', 'bonus_rate', 'team']
    list_filter = ['team']
    search_fields = ['name']


@admin.register(AccountSales)
class AccountSalesAdmin(admin.ModelAdmin):
    list_display = ['platform', 'platform_base', 'account_name', 'manager', 'month', 'ori_currency', 'currency_rate']
    list_filter = ['platform']
    search_fields = ['account_name']


@admin.register(AccountBonus)
class AccountBonusAdmin(admin.ModelAdmin):
    list_display = ['platform', 'platform_base', 'account_name', 'manager', 'month']
    list_filter = ['platform']
    search_fields = ['account_name']


@admin.register(Accounts)
class AccountsAdmin(admin.ModelAdmin):
    list_display = ['type', 'name', 'note']
    list_filter = ['type']
    search_fields = ['name']


@admin.register(MonthList)
class MonthListAdmin(admin.ModelAdmin):
    list_display = ['month', 'status']
    list_filter = ['status']
    search_fields = ['month']