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

from product.views import ProductViewSet, ProductExtraInfoViewSet, DeviceModelViewSet, CompatibleModelViewSet, \
    ProductTagViewSet, SupplierViewSet
from purchase.views import PurchaseOrderViewSet, PurchaseDetailViewSet, PurchaseOrderTagViewSet
from sale.views import CustomerDiscountViewSet, CustomerViewSet, CustomerTagViewSet
from setting.views import TagViewSet, OperateLogViewSet

from rest_framework.routers import DefaultRouter

from store.views import StoreViewSet, StockInOutViewSet

router = DefaultRouter()

# ---------------------------产品模块-------------------------------------------------
# 产品列表
router.register('products', ProductViewSet, basename='products')
# 产品附属信息
router.register('product_extra_info', ProductExtraInfoViewSet, basename='product_extra_info')
# 市面手机型号表
router.register('device_models', DeviceModelViewSet, basename='device_models')
# 产品兼容手机型号
router.register('comp_models', CompatibleModelViewSet, basename='comp_models')
# 产品标签
router.register('product_tags', ProductTagViewSet, basename='product_tags')
# 产品标签
router.register('suppliers', SupplierViewSet, basename='suppliers')

# ---------------------------系统设置-------------------------------------------------
# 标签库
router.register('settings/tags', TagViewSet, basename='tags')
# 操作日志
router.register('settings/op_logs', OperateLogViewSet, basename='op_logs')

# ---------------------------仓库/商店模块 -------------------------------------------------
# 仓库、销售门店
router.register('stores', StoreViewSet, basename='stores')
# 手工出入库/调拨
router.register('stock_in_out', StockInOutViewSet, basename='stock_in_out')

# ---------------------------采购模块 -------------------------------------------------
# 采购单
router.register('purchase_orders', PurchaseOrderViewSet, basename='purchase_orders')
# 采购单详细产品添加，修改，删除
router.register('purchase_detail', PurchaseDetailViewSet, basename='purchase_detail')
# 采购单标签
router.register('purchase_order_tags', PurchaseOrderTagViewSet, basename='purchase_order_tags')

# ---------------------------销售模块 -------------------------------------------------
# 客户专属优惠
router.register('customer_discount', CustomerDiscountViewSet, basename='customer_discount')
# 客户
router.register('customers', CustomerViewSet, basename='customers')
# 客户标签
router.register('customer_tags', CustomerTagViewSet, basename='customer_tags')

urlpatterns = [
    path('admin/', admin.site.urls),  # 管理员账号: admin 密码: admin123456
    path('api-token-auth/', obtain_jwt_token),
    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),  # 配置media root
    path('api/', include(router.urls)),
]
