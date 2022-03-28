from django.contrib import admin

from .models import Product, ProductExtraInfo, DeviceModel, CompatibleModel, ProductTag
# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'p_name', 'status', 'create_time']
    list_filter = ['status']
    search_fields = ['sku', 'p_name']


@admin.register(ProductExtraInfo)
class ProductExtraInfoAdmin(admin.ModelAdmin):
    list_display = ['type', 'name']
    list_filter = ['type']
    search_fields = ['name']


@admin.register(DeviceModel)
class DeviceModelAdmin(admin.ModelAdmin):
    list_display = ['brand', 'type', 'model']
    list_filter = ['type']
    search_fields = ['model']


@admin.register(CompatibleModel)
class CompatibleModelAdmin(admin.ModelAdmin):
    list_display = ['product', 'phone_model']


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ['product', 'tag']
