from django.contrib import admin
from devproduct.models import DevProduct, DevPrice, DevListingChannel, DevListingAccount, DevChannelData


# Register your models here.
@admin.register(DevProduct)
class DevProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'cn_name', 'p_status', 'create_time']
    list_filter = ['p_status']
    search_fields = ['sku', 'cn_name']


@admin.register(DevPrice)
class DevPriceAdmin(admin.ModelAdmin):
    list_display = ['platform', 'site', 'currency', 'price']
    list_filter = ['platform']
    search_fields = ['platform']


@admin.register(DevListingChannel)
class DevListingChannelAdmin(admin.ModelAdmin):
    list_display = ['platform', 'site', 'is_active']
    list_filter = ['platform']
    search_fields = ['platform']


@admin.register(DevListingAccount)
class DevListingAccountAdmin(admin.ModelAdmin):
    list_display = [
        'platform', 'user_name', 'account_name', 'is_online', 'create_time',
        'online_time'
    ]
    list_filter = ['user_name', 'is_online']
    search_fields = ['platform']


@admin.register(DevChannelData)
class DevChannelDataAdmin(admin.ModelAdmin):
    list_display = ['platform', 'site', 'default_active']
    list_filter = ['platform']
    search_fields = ['platform']
