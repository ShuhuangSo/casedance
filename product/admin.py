from django.contrib import admin

from mercado.models import MLProduct
from .models import Product, ProductExtraInfo, DeviceModel, CompatibleModel, ProductTag, Supplier, DeviceBrand


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
    list_display = ['brand', 'type', 'model', 'cp_id', 'image', 'dimensions', 'weight', 'link', 'announced', 'status', 'detail_model', 'create_time']
    list_filter = ['brand']
    search_fields = ['model']


@admin.register(CompatibleModel)
class CompatibleModelAdmin(admin.ModelAdmin):
    list_display = ['product', 'phone_model']


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ['product', 'tag']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['supplier_name']


@admin.register(DeviceBrand)
class DeviceBrandAdmin(admin.ModelAdmin):
    list_display = ['brand_name', 'link']
    search_fields = ['brand_name']


@admin.register(MLProduct)
class MLProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'sku', 'p_name']
    search_fields = ['sku', 'p_name']
