from django.contrib import admin
from django.utils.html import format_html
from .models import (BaseProductGroup, ProductGroup, ProductCore, ProductShop,
                     ProductImage, FetchTask)


# ------------------------------------------------------------------------------
# 产品图片 内联
# ------------------------------------------------------------------------------
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ('image_url', 'sort', 'is_cover', 'image_preview')
    readonly_fields = ('image_preview', )

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width:45px;height:45px;object-fit:cover;border-radius:4px" />',
                obj.image_url)
        return '-'

    image_preview.short_description = '预览'


# ------------------------------------------------------------------------------
# 基础产品组
# ------------------------------------------------------------------------------
@admin.register(BaseProductGroup)
class BaseProductGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'p_status', 'category', 'supplier', 'series',
                    'creator', 'create_time')
    list_filter = ('p_status', 'category', 'supplier', 'creator')
    search_fields = ('tag', 'note', 'category', 'supplier', 'series')
    readonly_fields = ('create_time', )
    inlines = [ProductImageInline]


# ------------------------------------------------------------------------------
# 店铺 SKU 内联（在 ProductGroup 里直接编辑）
# ------------------------------------------------------------------------------
class ProductShopInline(admin.TabularInline):
    model = ProductShop
    extra = 0
    fields = ('core_sku', 'title', 'price', 'currency', 'var1', 'var2', 'var3',
              'var4')
    readonly_fields = ()
    raw_id_fields = ('core_sku', )


# ------------------------------------------------------------------------------
# 店铺产品组
# ------------------------------------------------------------------------------
@admin.register(ProductGroup)
class ProductGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'base', 'shop_account', 'platform', 'site',
                    'variant_name')
    list_filter = ('platform', 'site', 'shop_account')
    search_fields = ('title', 'shop_account', 'desc', 'variant_name')
    raw_id_fields = ('base', )
    inlines = [ProductShopInline, ProductImageInline]


# ------------------------------------------------------------------------------
# 核心 SKU（全局唯一）
# ------------------------------------------------------------------------------
@admin.register(ProductCore)
class ProductCoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'sku', 'p_name', 'base', 'cost', 'UPC',
                    'purchase_url')
    list_filter = ('base__category', )
    search_fields = ('sku', 'p_name', 'UPC')
    raw_id_fields = ('base', )
    inlines = [ProductImageInline]


# ------------------------------------------------------------------------------
# 店铺维度 SKU
# ------------------------------------------------------------------------------
@admin.register(ProductShop)
class ProductShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'core_sku', 'group', 'title', 'price', 'currency')
    list_filter = ('group__platform', 'group__site', 'group__shop_account')
    search_fields = ('core_sku__sku', 'core_sku__p_name', 'title', 'var1',
                     'var2', 'var3', 'var4')
    raw_id_fields = ('group', 'core_sku')


# ------------------------------------------------------------------------------
# 产品图片
# ------------------------------------------------------------------------------
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image_preview', 'sort', 'is_cover', 'base_group',
                    'group', 'product_core')
    list_filter = ('is_cover', )
    search_fields = ('image_url', )
    readonly_fields = ('image_preview', )

    def image_preview(self, obj):
        if obj.image_url:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;object-fit:cover" />',
                obj.image_url)
        return '-'

    image_preview.short_description = '图片'


# ------------------------------------------------------------------------------
# 抓取任务
# ------------------------------------------------------------------------------
@admin.register(FetchTask)
class FetchTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_id', 'platform', 'marketplace_id', 'status',
                    'create_time')
    list_filter = ('status', 'platform')
    search_fields = ('item_id', 'log')
