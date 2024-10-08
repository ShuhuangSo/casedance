"""casedance URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls import include
from django.views.static import serve
from django.conf import settings
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.documentation import include_docs_urls

from bonus.views import AccountSalesViewSet, AccountBonusViewSet, AccountsViewSet, MonthListViewSet, \
    ExchangeRateViewSet, BasicInfoViewSet, ManagerViewSet
from mercado.views import ListingViewSet, ListingTrackViewSet, CategoriesViewSet, SellerViewSet, SellerTrackViewSet, \
    MLProductViewSet, ShopViewSet, ShopStockViewSet, ShipViewSet, ShipDetailViewSet, ShipBoxViewSet, CarrierViewSet, \
    TransStockViewSet, MLSiteViewSet, FBMWarehouseViewSet, MLOrderViewSet, FinanceViewSet, PackingViewSet, \
    MLOperateLogViewSet, ShopReportViewSet, PurchaseManageViewSet, ShipItemRemoveViewSet, ShipAttachmentViewSet, \
    UPCViewSet, RefillSettingsViewSet, RefillRecommendViewSet, CarrierTrackViewSet, MLStockLogViewSet, \
    FileUploadNotifyViewSet, PlatformCategoryRateViewSet
from product.views import ProductViewSet, ProductExtraInfoViewSet, DeviceModelViewSet, CompatibleModelViewSet, \
    ProductTagViewSet, SupplierViewSet, SimpleProductViewSet, DeviceBrandViewSet
from purchase.views import PurchaseOrderViewSet, PurchaseDetailViewSet, PurchaseOrderTagViewSet, RefillPromoteViewSet
from report.views import SalesReportViewSet, StockReportViewSet, CustomerReportViewSet, ProductReportViewSet
from sale.views import CustomerDiscountViewSet, CustomerViewSet, CustomerTagViewSet, OrderViewSet, OrderDetailViewSet, \
    OrderTagViewSet
from setting.views import TagViewSet, OperateLogViewSet, MenuViewSet, UserViewSet, AllMenuViewSet, UserMenuViewSet, \
    SysRefillViewSet, AllMLUserPermissionViewSet, MLUserPermissionViewSet, MLPermissionViewSet

from rest_framework.routers import DefaultRouter

from store.views import StoreViewSet, StockInOutViewSet, StockLogViewSet, StockViewSet
from devproduct.views import DevProductViewSet, DevPriceViewSet, DevChannelDataViewSet, DevListingChannelViewSet, DevListingAccountViewSet, DevOrderViewSet

router = DefaultRouter()

# ---------------------------产品模块-------------------------------------------------
# 产品列表
router.register('products', ProductViewSet, basename='products')
# 简易产品列表
router.register('simple_products',
                SimpleProductViewSet,
                basename='simple_products')
# 产品附属信息
router.register('product_extra_info',
                ProductExtraInfoViewSet,
                basename='product_extra_info')
# 市面手机型号表
router.register('device_models', DeviceModelViewSet, basename='device_models')
# 市面手机品牌
router.register('device_brands', DeviceBrandViewSet, basename='device_brands')
# 产品兼容手机型号
router.register('comp_models', CompatibleModelViewSet, basename='comp_models')
# 产品标签
router.register('product_tags', ProductTagViewSet, basename='product_tags')
# 供应商
router.register('suppliers', SupplierViewSet, basename='suppliers')

# ---------------------------系统设置-------------------------------------------------
# 标签库
router.register('settings/tags', TagViewSet, basename='tags')
# 操作日志
router.register('settings/op_logs', OperateLogViewSet, basename='op_logs')
# 当前用户菜单
router.register('settings/menu', MenuViewSet, basename='menu')
# 所有菜单
router.register('settings/all_menu', AllMenuViewSet, basename='all_menu')
# 指定用户菜单
router.register('settings/user_menu', UserMenuViewSet, basename='user_menu')
# 用户信息
router.register('settings/users', UserViewSet, basename='users')
# 用户信息
router.register('settings/sys_refill', SysRefillViewSet, basename='sys_refill')
# 所有美客多操作权限
router.register('settings/all_ml_permission',
                AllMLUserPermissionViewSet,
                basename='all_ml_permission')
# 指定用户美客多操作权限
router.register('settings/user_ml_permission',
                MLUserPermissionViewSet,
                basename='user_ml_permission')
# 前端指定用户美客多操作权限
router.register('settings/get_ml_permission',
                MLPermissionViewSet,
                basename='get_ml_permission')

# ---------------------------仓库/商店模块 -------------------------------------------------
# 仓库、销售门店
router.register('stores', StoreViewSet, basename='stores')
# 手工出入库/调拨
router.register('stock_in_out', StockInOutViewSet, basename='stock_in_out')
# 库存出入日志
router.register('stock_log', StockLogViewSet, basename='stock_log')
# 库存列表
router.register('stock_list', StockViewSet, basename='stock_list')

# ---------------------------采购模块 -------------------------------------------------
# 采购单
router.register('purchase_orders',
                PurchaseOrderViewSet,
                basename='purchase_orders')
# 采购单详细产品添加，修改，删除
router.register('purchase_detail',
                PurchaseDetailViewSet,
                basename='purchase_detail')
# 采购单标签
router.register('purchase_order_tags',
                PurchaseOrderTagViewSet,
                basename='purchase_order_tags')
# 采购推荐
router.register('refill_promote',
                RefillPromoteViewSet,
                basename='refill_promote')

# ---------------------------销售模块 -------------------------------------------------
# 客户专属优惠
router.register('customer_discount',
                CustomerDiscountViewSet,
                basename='customer_discount')
# 客户
router.register('customers', CustomerViewSet, basename='customers')
# 客户标签
router.register('customer_tags', CustomerTagViewSet, basename='customer_tags')
# 销售订单
router.register('orders', OrderViewSet, basename='orders')
# 销售订单明细
router.register('order_detail', OrderDetailViewSet, basename='order_detail')
# 销售订单标签
router.register('order_tags', OrderTagViewSet, basename='order_tags')
# ---------------------------报告模块-------------------------------------------------
# 销量统计
router.register('sales_report', SalesReportViewSet, basename='sales_report')
# 库存统计
router.register('stock_report', StockReportViewSet, basename='stock_report')
# 客户销量统计报告
router.register('customer_report',
                CustomerReportViewSet,
                basename='customer_report')
# 统计产品每天销量
router.register('product_report',
                ProductReportViewSet,
                basename='product_report')
# ---------------------------销售业绩app-------------------------------------------------
# 账号销售报表
router.register('bo_account_sales',
                AccountSalesViewSet,
                basename='bo_account_sales')
# 提成表
router.register('bo_account_bonus',
                AccountBonusViewSet,
                basename='bo_account_bonus')
# 帐号
router.register('bo_bonus_accounts',
                AccountsViewSet,
                basename='bo_bonus_accounts')
# 统计月份
router.register('bo_month_list', MonthListViewSet, basename='bo_month_list')
# 汇率
router.register('bo_exchange_rate',
                ExchangeRateViewSet,
                basename='bo_exchange_rate')
# 基础信息
router.register('bo_basic_info', BasicInfoViewSet, basename='bo_basic_info')
# 运营负责人
router.register('bo_manager', ManagerViewSet, basename='bo_manager')
# ---------------------------美客多app-------------------------------------------------
# 在线产品列表
router.register('med_listing', ListingViewSet, basename='med_listing')
# 商品跟踪
router.register('med_listing_track',
                ListingTrackViewSet,
                basename='med_listing_track')
# 站点类目列表
router.register('med_categories', CategoriesViewSet, basename='med_categories')
# 卖家
router.register('med_seller', SellerViewSet, basename='med_seller')
# 卖家跟踪
router.register('med_seller_track',
                SellerTrackViewSet,
                basename='med_seller_track')
# ML产品列表
router.register('ml_products', MLProductViewSet, basename='ml_products')
# FBM店铺列表
router.register('ml_shops', ShopViewSet, basename='ml_shops')
# 店铺库存列表
router.register('ml_shopstock', ShopStockViewSet, basename='ml_shopstock')
# 头程运单列表
router.register('ml_ship', ShipViewSet, basename='ml_ship')
# 头程运单详情列表
router.register('ml_ship_detail', ShipDetailViewSet, basename='ml_ship_detail')
# 遗弃清单列表
router.register('ml_ship_item_remove',
                ShipItemRemoveViewSet,
                basename='ml_ship_item_remove')
# 运单附件列表
router.register('ml_ship_attachment',
                ShipAttachmentViewSet,
                basename='ml_ship_attachment')
# 运单物流跟踪列表
router.register('ml_ship_tracking',
                CarrierTrackViewSet,
                basename='ml_ship_tracking')
# 头程包装箱列表
router.register('ml_ship_box', ShipBoxViewSet, basename='ml_ship_box')
# 物流商列表
router.register('ml_carriers', CarrierViewSet, basename='ml_carriers')
# 中转仓库存列表,
router.register('ml_trans_stock', TransStockViewSet, basename='ml_trans_stock')
# 站点列表,
router.register('ml_site', MLSiteViewSet, basename='ml_site')
# FBM仓库列表,
router.register('ml_fbm_warehouse',
                FBMWarehouseViewSet,
                basename='ml_fbm_warehouse')
# FBM销售订单列表,
router.register('ml_orders', MLOrderViewSet, basename='ml_orders')
# 财务管理列表,
router.register('ml_finance', FinanceViewSet, basename='ml_finance')
# 包材管理列表,
router.register('ml_packing', PackingViewSet, basename='ml_packing')
# 操作日志列表,
router.register('ml_operate_log',
                MLOperateLogViewSet,
                basename='ml_operate_log')
# 店铺销量统计列表,
router.register('ml_shop_reports',
                ShopReportViewSet,
                basename='ml_shop_reports')
# 采购管理列表,
router.register('ml_purchase', PurchaseManageViewSet, basename='ml_purchase')
# UPC号码池列表,
router.register('upc_manage', UPCViewSet, basename='upc_manage')
# 补货推荐设置列表,
router.register('ml_refill_settings',
                RefillSettingsViewSet,
                basename='ml_refill_settings')
# 补货推荐列表,
router.register('ml_refill', RefillRecommendViewSet, basename='ml_refill')
# 库存日志列表,
router.register('ml_stock_log', MLStockLogViewSet, basename='ml_stock_log')
# 文件上传通知列表,
router.register('ml_file_upload_notify',
                FileUploadNotifyViewSet,
                basename='ml_file_upload_notify')
# 平台类目佣金费率列表,
router.register('platform_category',
                PlatformCategoryRateViewSet,
                basename='platform_category')
# ---------------------------产品开发app-------------------------------------------------
# 产品开发列表
router.register('dev_products', DevProductViewSet, basename='dev_products')
# 产品开发定价列表
router.register('dev_product_price',
                DevPriceViewSet,
                basename='dev_product_price')
# 开发平台渠道数据列表
router.register('dev_channel_data',
                DevChannelDataViewSet,
                basename='dev_channel_data')
# 开发产品发布渠道列表
router.register('dev_channel',
                DevListingChannelViewSet,
                basename='dev_channel')
# 开发产品上架账号列表
router.register('dev_listing_account',
                DevListingAccountViewSet,
                basename='dev_listing_account')
# 开发产品订单列表
router.register('dev_order', DevOrderViewSet, basename='dev_order')

urlpatterns = [
    path('admin/', admin.site.urls),  # 管理员账号: admin 密码: admin123456
    path('docs/', include_docs_urls(title='CaseDance项目接口文档')),
    path('api-token-auth/', obtain_jwt_token),
    re_path(r'media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT}),  # 配置media root
    path('api/', include(router.urls)),
]
