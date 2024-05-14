from django.contrib import admin

from mercado.models import Listing, ListingTrack, ApiSetting, Seller, Categories, TransApiSetting, Keywords, \
    SellerTrack, Shop, ShopStock, Ship, ShipDetail, ShipBox, TransStock, MLSite, FBMWarehouse, MLOrder, ExRate, Finance, \
    Packing, MLOperateLog, ShopReport, PurchaseManage, UPC, RefillRecommend, RefillSettings, CarrierTrack, \
    GeneralSettings


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'title', 'total_sold', 'update_time']
    list_filter = ['seller_name']
    search_fields = ['item_id', 'seller_name']


@admin.register(ListingTrack)
class ListingTrackAdmin(admin.ModelAdmin):
    list_display = ['listing', 'today_sold', 'reviews', 'stock_num', 'create_time']


@admin.register(ApiSetting)
class ApiSettingAdmin(admin.ModelAdmin):
    list_display = ['access_token']


@admin.register(TransApiSetting)
class TransApiSettingAdmin(admin.ModelAdmin):
    list_display = ['appid', 'secretKey']


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['seller_id', 'nickname', 'total', 'registration_date']


@admin.register(SellerTrack)
class SellerTrackAdmin(admin.ModelAdmin):
    list_display = ['seller', 'today_sold', 'total_items', 'total', 'create_time']


@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ['categ_id', 'father_id', 'site_id', 'name', 't_name']
    list_filter = ['site_id', 'father_id']
    search_fields = ['name', 't_name']


@admin.register(Keywords)
class KeywordsAdmin(admin.ModelAdmin):
    list_display = ['categ_id', 'keyword', 'rank', 'status', 'rank_changed', 'update_time']
    list_filter = ['categ_id']
    search_fields = ['keyword', 't_keyword']


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'nickname', 'seller_id']
    list_filter = ['warehouse_type']
    search_fields = ['name', 'nickname', 'seller_id']


@admin.register(ShopStock)
class ShopStockAdmin(admin.ModelAdmin):
    list_display = ['sku', 'p_name', 'qty']
    list_filter = ['p_status', 'shop']
    search_fields = ['sku', 'p_name']


@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = ['batch', 'envio_number', 'shop']
    list_filter = ['s_status']
    search_fields = ['batch', 'envio_number']


@admin.register(ShipDetail)
class ShipDetailAdmin(admin.ModelAdmin):
    list_display = ['sku', 'p_name', 'qty']
    list_filter = ['ship']
    search_fields = ['sku', 'p_name']


@admin.register(ShipBox)
class ShipBoxAdmin(admin.ModelAdmin):
    list_display = ['box_number', 'carrier_box_number', 'item_qty']
    list_filter = ['ship']
    search_fields = ['box_number', 'carrier_box_number']


@admin.register(TransStock)
class TransStockAdmin(admin.ModelAdmin):
    list_display = ['box_number', 'carrier_box_number', 'sku']
    search_fields = ['box_number', 'sku']


@admin.register(MLSite)
class TransStockAdmin(admin.ModelAdmin):
    list_display = ['od_num', 'site_code', 'name']
    search_fields = ['name', 'site_code']


@admin.register(FBMWarehouse)
class FBMWarehouseStockAdmin(admin.ModelAdmin):
    list_display = ['w_code', 'name', 'country']
    search_fields = ['name', 'w_code']


@admin.register(MLOrder)
class MLOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'sku', 'qty']
    search_fields = ['sku', 'order_number']


@admin.register(ExRate)
class ExRateAdmin(admin.ModelAdmin):
    list_display = ['currency', 'value', 'update_time']


@admin.register(Finance)
class FinanceAdmin(admin.ModelAdmin):
    list_display = ['shop', 'currency', 'income', 'is_received', 'wd_date', 'rec_date']
    list_filter = ['f_type', 'shop']


@admin.register(Packing)
class PackingAdmin(admin.ModelAdmin):
    list_display = ['name', 'size', 'weight']


@admin.register(MLOperateLog)
class MLOperateLogAdmin(admin.ModelAdmin):
    list_display = ['op_module', 'desc', 'user', 'create_time']
    list_filter = ['op_module']


@admin.register(ShopReport)
class ShopReportAdmin(admin.ModelAdmin):
    list_display = ['qty', 'amount', 'calc_date']
    list_filter = ['shop']


@admin.register(PurchaseManage)
class PurchaseManageAdmin(admin.ModelAdmin):
    list_display = ['sku', 'p_name', 'p_status']
    list_filter = ['p_status']
    search_fields = ['sku']


@admin.register(UPC)
class UPCAdmin(admin.ModelAdmin):
    list_display = ['number', 'is_used', 'create_time']
    list_filter = ['is_used']
    search_fields = ['number']


@admin.register(RefillRecommend)
class RefillRecommendAdmin(admin.ModelAdmin):
    list_display = ['sku', 'min_send', 'full_send', 'create_time']
    list_filter = ['is_new']
    search_fields = ['sku']


@admin.register(RefillSettings)
class RefillSettingsAdmin(admin.ModelAdmin):
    list_display = ['fly_days', 'fly_batch_period', 'is_include_trans', 'platform']
    list_filter = ['is_include_trans']


@admin.register(CarrierTrack)
class CarrierTrackAdmin(admin.ModelAdmin):
    list_display = ['carrier_number', 'context', 'time', 'create_time']
    list_filter = ['carrier_name']
    search_fields = ['carrier_number']


@admin.register(GeneralSettings)
class GeneralSettingsAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'update_time']
    search_fields = ['item_name']