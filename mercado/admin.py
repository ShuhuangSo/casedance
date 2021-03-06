from django.contrib import admin

from mercado.models import Listing, ListingTrack, ApiSetting, Seller, Categories, TransApiSetting, Keywords, SellerTrack


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