from rest_framework import serializers
from datetime import datetime, timedelta
from xToolkit import xstring
from django.db.models import Q

from casedance.settings import BASE_URL, MEDIA_URL
from mercado.models import Listing, ListingTrack, Categories, Seller, SellerTrack, MLProduct, Shop, ShopStock, Ship, \
    ShipDetail, ShipBox, Carrier, TransStock, MLSite, FBMWarehouse, MLOrder, Finance, Packing, MLOperateLog, ShopReport, \
    PurchaseManage, ShipItemRemove, ShipAttachment, UPC, RefillRecommend, RefillSettings, CarrierTrack


class ListingSerializer(serializers.ModelSerializer):
    """
    在线产品
    """
    sold_7d = serializers.SerializerMethodField()
    sold_7d_grow = serializers.SerializerMethodField()
    sold_30d = serializers.SerializerMethodField()
    sold_30d_grow = serializers.SerializerMethodField()
    yesterday_sold = serializers.SerializerMethodField()
    yesterday_sold_grow = serializers.SerializerMethodField()

    # 获取7天销量
    def get_sold_7d(self, obj):
        start_date = datetime.now() - timedelta(days=7)
        lt = ListingTrack.objects.filter(create_time__gte=start_date, listing=obj)
        n = 0
        for i in lt:
            n += i.today_sold
        return n

    def get_yesterday_sold(self, obj):
        date = datetime.now().date() - timedelta(days=1)
        lt = ListingTrack.objects.filter(create_time__date=date, listing=obj).first()
        n = lt.today_sold if lt else 0
        return n

    def get_yesterday_sold_grow(self, obj):
        date = datetime.now() - timedelta(days=1)
        last_date = date - timedelta(days=1)
        lt = ListingTrack.objects.filter(create_time__date=date, listing=obj).first()
        n = lt.today_sold if lt else 0

        lt2 = ListingTrack.objects.filter(create_time__date=last_date, listing=obj).first()
        m = lt2.today_sold if lt2 else 0

        p = n * 100 if m == 0 else int((n - m) / m * 100)
        return p

    # 获取上一个7天销量
    def get_sold_7d_grow(self, obj):
        start_date = datetime.now().date() - timedelta(days=7)
        last_start_date = start_date - timedelta(days=7)
        lt = ListingTrack.objects.filter(create_time__date__gte=start_date, listing=obj)
        n = 0
        for i in lt:
            n += i.today_sold

        lt2 = ListingTrack.objects.filter(create_time__date__gte=last_start_date, create_time__date__lt=start_date,
                                          listing=obj)
        m = 0
        for i in lt2:
            m += i.today_sold

        p = n * 100 if m == 0 else int((n - m) / m * 100)
        return p

    # 获取30天销量
    def get_sold_30d(self, obj):
        start_date = datetime.now().date() - timedelta(days=30)
        lt = ListingTrack.objects.filter(create_time__date__gte=start_date, listing=obj)
        n = 0
        for i in lt:
            n += i.today_sold
        return n

    # 获取上一个30天销量
    def get_sold_30d_grow(self, obj):
        start_date = datetime.now().date() - timedelta(days=30)
        last_start_date = start_date - timedelta(days=30)
        lt = ListingTrack.objects.filter(create_time__date__gte=start_date, listing=obj)
        n = 0
        for i in lt:
            n += i.today_sold

        lt2 = ListingTrack.objects.filter(create_time__date__gte=last_start_date, create_time__date__lt=start_date,
                                          listing=obj)
        m = 0
        for i in lt2:
            m += i.today_sold

        p = n * 100 if m == 0 else int((n - m) / m * 100)
        return p

    class Meta:
        model = Listing
        fields = ('id', 'item_id', 'site_id', 'title', 'image', 'link', 'price', 'currency', 'total_sold', 'sold_7d',
                  'sold_30d', 'reviews', 'rating_average', 'start_date', 'listing_status', 'health', 'stock_num',
                  'ship_type', 'is_cbt', 'is_free_shipping', 'seller_id', 'seller_name', 'brand', 'collection',
                  'cost', 'profit', 'note', 'create_time', 'update_time', 'sold_7d_grow', 'sold_30d_grow',
                  'yesterday_sold', 'yesterday_sold_grow')


class ListingTrackSerializer(serializers.ModelSerializer):
    """
    商品跟踪
    """
    create_time = serializers.DateTimeField(format='%Y-%m-%d')

    class Meta:
        model = ListingTrack
        fields = "__all__"


class CategoriesSerializer(serializers.ModelSerializer):
    """
    站点类目
    """

    class Meta:
        model = Categories
        fields = "__all__"


class SellerSerializer(serializers.ModelSerializer):
    """
    卖家
    """
    yesterday_sold = serializers.SerializerMethodField()

    def get_yesterday_sold(self, obj):
        date = datetime.now().date() - timedelta(days=1)
        st = SellerTrack.objects.filter(create_time__date=date, seller=obj).first()
        n = st.today_sold if st else 0
        return n

    class Meta:
        model = Seller
        fields = ('id', 'seller_id', 'site_id', 'nickname', 'level_id', 'total', 'canceled', 'negative', 'neutral',
                  'positive', 'registration_date', 'link', 'sold_60d', 'total_items', 'collection', 'update_time',
                  'note', 'yesterday_sold')


class SellerTrackSerializer(serializers.ModelSerializer):
    """
    卖家跟踪
    """
    create_time = serializers.DateTimeField(format='%Y-%m-%d')

    class Meta:
        model = SellerTrack
        fields = "__all__"


class MLProductSerializer(serializers.ModelSerializer):
    """
    mercado产品库
    """
    is_incomplete = serializers.SerializerMethodField()  # 是否不完整

    def get_is_incomplete(self, obj):
        status = False

        if not (obj.site and obj.item_id and obj.unit_cost and obj.image and obj.shop):
            status = True
        if not (
                obj.custom_code and obj.cn_name and obj.en_name and obj.brand and obj.declared_value and obj.cn_material and obj.en_material):
            status = True
        if not (obj.use and obj.weight and obj.length and obj.width and obj.heigth and obj.first_ship_cost):
            status = True
        return status

    class Meta:
        model = MLProduct
        fields = ('id', 'sku', 'p_name', 'label_code', 'upc', 'item_id', 'image', 'p_status', 'custom_code', 'cn_name',
                  'en_name', 'brand', 'declared_value', 'cn_material', 'en_material', 'use', 'site', 'shop',
                  'unit_cost', 'is_elec', 'is_magnet', 'is_water',
                  'first_ship_cost', 'length', 'width', 'heigth', 'weight', 'buy_url', 'sale_url', 'refer_url', 'note',
                  'create_time', 'is_checked', 'label_title', 'label_option', 'packing_id', 'buy_url2', 'buy_url3',
                  'buy_url4', 'buy_url5', 'user_id', 'is_incomplete', 'platform')


class ShopSerializer(serializers.ModelSerializer):
    """
    FBM店铺
    """

    class Meta:
        model = Shop
        fields = "__all__"


class ShopStockSerializer(serializers.ModelSerializer):
    """
    店铺库存
    """
    preparing_qty = serializers.SerializerMethodField()  # 运单备货数量
    p_onway_qty = serializers.SerializerMethodField()  # 采购在途数量
    p_rec_qty = serializers.SerializerMethodField()  # 采购到货数量
    fbm_onway_qty = serializers.SerializerMethodField()  # fbm在途数量
    trans_onway_qty = serializers.SerializerMethodField()  # 中转在途数量

    def get_trans_onway_qty(self, obj):
        qty = 0
        queryset = ShipDetail.objects.filter(sku=obj.sku, ship__target='TRANSIT').filter(Q(ship__s_status='SHIPPED') | Q(ship__s_status='BOOKED'))
        for i in queryset:
            qty += i.qty
        return qty

    def get_fbm_onway_qty(self, obj):
        qty = 0
        queryset = ShipDetail.objects.filter(sku=obj.sku, ship__target='FBM').filter(Q(ship__s_status='SHIPPED') | Q(ship__s_status='BOOKED'))
        for i in queryset:
            qty += i.qty
        return qty

    # 备货中数量
    def get_preparing_qty(self, obj):
        qty = 0
        queryset = ShipDetail.objects.filter(sku=obj.sku, item_id=obj.item_id, ship__s_status='PREPARING')
        for i in queryset:
            qty += i.qty
        return qty

    # 采购中数量
    def get_p_onway_qty(self, obj):
        qty = 0
        queryset = PurchaseManage.objects.filter(sku=obj.sku, p_status='PURCHASED')
        for i in queryset:
            qty += i.buy_qty
        return qty

    # 采购到货数量
    def get_p_rec_qty(self, obj):
        qty = 0
        queryset = PurchaseManage.objects.filter(sku=obj.sku).filter(Q(p_status='RECEIVED') | Q(p_status='PACKED'))
        for i in queryset:
            if i.p_status == 'RECEIVED':
                qty += i.rec_qty
            if i.p_status == 'PACKED':
                qty += i.pack_qty
        return qty

    class Meta:
        model = ShopStock
        fields = (
            'id', 'shop', 'sku', 'p_name', 'label_code', 'upc', 'item_id',
            'image', 'p_status', 'qty', 'fbm_onway_qty', 'trans_onway_qty', 'trans_qty', 'day7_sold', 'day15_sold', 'day30_sold',
            'total_sold', 'unit_cost', 'first_ship_cost', 'length', 'width', 'heigth', 'weight', 'total_profit',
            'total_weight', 'total_cbm', 'stock_value', 'refund_rate', 'avg_profit', 'avg_profit_rate', 'sale_url',
            'note', 'create_time', 'is_active', 'is_collect', 'preparing_qty', 'p_onway_qty', 'p_rec_qty')


class ShipDetailSerializer(serializers.ModelSerializer):
    """
    运单详情
    """
    total_onway_qty = serializers.SerializerMethodField()
    total_rec_qty = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()

    def get_total_onway_qty(self, obj):
        qty = 0
        queryset = PurchaseManage.objects.filter(sku=obj.sku, p_status='PURCHASED')
        for i in queryset:
            qty += i.buy_qty
        return qty

    def get_total_rec_qty(self, obj):
        qty = 0
        queryset = PurchaseManage.objects.filter(sku=obj.sku).filter(Q(p_status='RECEIVED') | Q(p_status='PACKED'))
        for i in queryset:
            if i.p_status == 'RECEIVED':
                qty += i.rec_qty
            if i.p_status == 'PACKED':
                qty += i.pack_qty
        return qty

    def get_user_id(self, obj):
        shop = Shop.objects.filter(name=obj.target_FBM).first()
        user_id = None
        if shop:
            if shop.user:
                user_id = shop.user.id
        return user_id

    class Meta:
        model = ShipDetail
        fields = (
            'id', 'target_FBM', 'box_number', 's_type', 'sku', 'p_name', 'label_code', 'upc', 'item_id',
            'image', 'custom_code', 'cn_name', 'en_name', 'brand', 'declared_value', 'cn_material', 'en_material',
            'use', 'unit_cost', 'avg_ship_fee', 'qty', 'length', 'width', 'heigth', 'weight', 'note',
            'create_time', 'packing_name', 'packing_size', 'plan_qty', 'ship', 'total_onway_qty', 'total_rec_qty', 'user_id')


class ShipSerializer(serializers.ModelSerializer):
    """
    头程运单
    """
    # 运单详情
    ship_shipDetail = ShipDetailSerializer(many=True, required=False, read_only=True)

    fbm_name = serializers.SerializerMethodField()
    fbm_address = serializers.SerializerMethodField()
    shop_color = serializers.SerializerMethodField()
    book_days = serializers.SerializerMethodField()
    products_weight = serializers.SerializerMethodField()
    is_attach = serializers.SerializerMethodField()
    manager = serializers.SerializerMethodField()
    is_remove_items = serializers.SerializerMethodField()  # 是否有变动清单产品
    latest_track = serializers.SerializerMethodField()  # 最新跟踪信息

    def get_latest_track(self, obj):
        msg = ''
        if obj.s_number:
            ct = CarrierTrack.objects.filter(carrier_number=obj.s_number).order_by('-time').first()
            if ct:
                msg = ct.context

        return msg

    def get_is_remove_items(self, obj):
        is_exist = ShipItemRemove.objects.filter(ship=obj).count()

        return True if is_exist else False

    def get_products_weight(self, obj):
        queryset = ShipDetail.objects.filter(ship=obj)
        w = 0
        for i in queryset:
            w += i.weight * i.qty
        return w

    def get_book_days(self, obj):
        if obj.book_date:
            ad = str(obj.book_date)
            dd = datetime.strptime(ad, '%Y-%m-%d')
            delta = datetime.now() - dd
            return 0 - delta.days
        else:
            return 0

    def get_shop_color(self, obj):
        shop = Shop.objects.filter(name=obj.shop).first()
        return shop.name_color if shop else ''

    def get_fbm_name(self, obj):
        fbm = FBMWarehouse.objects.filter(w_code=obj.fbm_warehouse).first()
        if fbm:
            return fbm.name
        return ''

    def get_fbm_address(self, obj):
        fbm = FBMWarehouse.objects.filter(w_code=obj.fbm_warehouse).first()
        if fbm:
            return fbm.address
        return ''

    def get_is_attach(self, obj):
        sa = ShipAttachment.objects.filter(ship=obj).count()

        return True if sa else False

    def get_manager(self, obj):
        shop = Shop.objects.filter(name=obj.shop).first()
        manager = shop.user.first_name if shop.user else '管理员'  # 负责人
        return manager

    class Meta:
        model = Ship
        fields = (
            'id', 's_number', 'batch', 's_status', 'shop', 'shop_color', 'target', 'envio_number', 'ship_type',
            'shipping_fee', 'sent_time', 'platform',
            'extra_fee', 'fbm_warehouse', 'fbm_name', 'fbm_address', 'send_from', 'tag_name', 'tag_color',
            'carrier', 'end_date', 'ship_date', 'book_date', 'book_days', 'total_box', 'total_qty', 'weight', 'cbm',
            'note', 'create_time', 'products_cost', 'products_weight', 'user_id', 'manager', 'logi_fee_clear',
            'is_attach', 'is_remove_items', 'ship_shipDetail', 'latest_track')


class ShipBoxSerializer(serializers.ModelSerializer):
    """
    包装箱
    """

    class Meta:
        model = ShipBox
        fields = "__all__"


class ShipItemRemoveSerializer(serializers.ModelSerializer):
    """
    遗弃清单
    """
    batch = serializers.SerializerMethodField()
    shop = serializers.SerializerMethodField()
    shop_color = serializers.SerializerMethodField()

    def get_batch(self, obj):
        return obj.ship.batch

    def get_shop(self, obj):
        return obj.ship.shop

    def get_shop_color(self, obj):
        shop = Shop.objects.filter(name=obj.ship.shop).first()
        return shop.name_color if shop else ''

    class Meta:
        model = ShipItemRemove
        fields = ('id', 'item_type', 'sku', 'p_name', 'item_id', 'image', 'plan_qty', 'send_qty', 'note', 'create_time',
                  'handle', 'handle_time', 'ship', 'batch', 'shop', 'shop_color', 'belong_shop')


class ShipAttachmentSerializer(serializers.ModelSerializer):
    """
    运单附件
    """
    link = serializers.SerializerMethodField()

    def get_link(self, obj):
        path = '{batch}_{id}/{name}'.format(batch=obj.ship.batch, id=obj.ship.id, name=obj.name)
        url = BASE_URL + MEDIA_URL + 'ml_ships/' + path
        return url

    class Meta:
        model = ShipAttachment
        fields = ('id', 'ship', 'a_type', 'name', 'link', 'create_time')


class CarrierSerializer(serializers.ModelSerializer):
    """
    物流商
    """

    class Meta:
        model = Carrier
        fields = "__all__"


class TransStockSerializer(serializers.ModelSerializer):
    """
    中转仓库存
    """
    stock_days = serializers.SerializerMethodField()
    shop_color = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    def get_stock_days(self, obj):
        if obj.arrived_date:
            ad = str(obj.arrived_date)
            dd = datetime.strptime(ad, '%Y-%m-%d')
            delta = datetime.now() - dd
            return delta.days
        else:
            return 0

    def get_shop_color(self, obj):
        shop = Shop.objects.filter(name=obj.listing_shop).first()
        return shop.name_color if shop else ''

    def get_group(self, obj):
        count = TransStock.objects.filter(box_number=obj.box_number, is_out=False).count()
        return count if count > 1 else 0

    class Meta:
        model = TransStock
        fields = (
            'id', 'listing_shop', 'shop_color', 'sku', 'p_name', 'label_code', 'upc', 'item_id', 'image', 'qty',
            'unit_cost', 'first_ship_cost', 's_number', 'batch',
            'box_number', 'carrier_box_number', 'box_length', 'box_width', 'box_heigth', 'box_weight', 'box_cbm',
            'note',
            'arrived_date', 'is_out', 'shop', 'stock_days', 'group', 'user_id', 'out_time')


class MLSiteSerializer(serializers.ModelSerializer):
    """
    站点
    """

    class Meta:
        model = MLSite
        fields = "__all__"


class FBMWarehouseSerializer(serializers.ModelSerializer):
    """
    FBM仓库
    """

    class Meta:
        model = FBMWarehouse
        fields = "__all__"


class MLOrderSerializer(serializers.ModelSerializer):
    """
    销售订单
    """
    sale_url = serializers.SerializerMethodField()

    def get_sale_url(self, obj):
        url = ''
        if obj.shop.platform == 'MERCADO':
            url = 'https://articulo.mercadolibre.com.mx/' + obj.shop.site + '-' + obj.item_id
        if obj.shop.platform == 'NOON':
            if obj.shop.site == 'KSA':
                url = 'https://www.noon.com/saudi-en/product/{item_id}/p/?o={item_id}-1'.format(item_id=obj.item_id)
        return url

    class Meta:
        model = MLOrder
        fields = ('id', 'order_number', 'order_status', 'order_time', 'order_time_bj', 'qty', 'currency', 'ex_rate',
                  'price', 'fees', 'postage', 'receive_fund', 'profit', 'profit_rate', 'is_ad', 'sku', 'p_name',
                  'item_id', 'image', 'unit_cost', 'first_ship_cost', 'buyer_name', 'buyer_address', 'buyer_city',
                  'buyer_state', 'buyer_postcode', 'buyer_country', 'create_time', 'shop', 'sale_url', 'platform',
                  'buyer_id', 'shipped_date', 'delivered_date', 'VAT', 'invoice_price', 'promo_coupon')


class FinanceSerializer(serializers.ModelSerializer):
    """
    财务管理
    """
    shop_name = serializers.SerializerMethodField()

    def get_shop_name(self, obj):
        shop_name = obj.shop.name
        return shop_name

    class Meta:
        model = Finance
        fields = ('id', 'shop', 'currency', 'income', 'wd_date', 'rec_date', 'exchange', 'income_rmb', 'exc_date',
                  'f_type', 'is_received', 'create_time', 'shop_name')


class PackingSerializer(serializers.ModelSerializer):
    """
    包材管理
    """

    class Meta:
        model = Packing
        fields = "__all__"


class MLOperateLogSerializer(serializers.ModelSerializer):
    """
    操作日志
    """
    user_name = serializers.SerializerMethodField()
    target_name = serializers.SerializerMethodField()

    def get_user_name(self, obj):

        return obj.user.first_name if obj.user else 'System'

    def get_target_name(self, obj):
        name = ''
        if obj.target_type == 'PRODUCT':
            if obj.target_id:
                product = MLProduct.objects.filter(id=obj.target_id).first()
                if product:
                    name = product.sku
        if obj.target_type == 'PACKING':
            name = '包材管理'

        if obj.target_type == 'SHIP':
            if obj.target_id:
                ship = Ship.objects.filter(id=obj.target_id).first()
                if ship:
                    name = ship.batch + '-' + ship.shop
        if obj.target_type == 'FBM':
            if obj.target_id:
                shop_stock = ShopStock.objects.filter(id=obj.target_id).first()
                if shop_stock:
                    name = shop_stock.sku

        return name

    class Meta:
        model = MLOperateLog
        fields = ('id', 'op_module', 'op_type', 'target_id', 'target_type', 'desc', 'user_name', 'create_time',
                  'target_name')


class ShopReportSerializer(serializers.ModelSerializer):
    """
    店铺销量统计
    """
    amount = serializers.SerializerMethodField()
    profit = serializers.SerializerMethodField()
    shop = serializers.SerializerMethodField()

    def get_amount(self, obj):
        return round(obj.amount, 2)

    def get_profit(self, obj):
        return round(obj.profit, 2)

    def get_shop(self, obj):
        return obj.shop.name

    class Meta:
        model = ShopReport
        fields = ('id', 'amount', 'profit', 'shop', 'calc_date', 'qty')


class PurchaseManageSerializer(serializers.ModelSerializer):
    """
    采购管理
    """
    need_qty = serializers.SerializerMethodField()
    total_onway_qty = serializers.SerializerMethodField()
    total_rec_qty = serializers.SerializerMethodField()
    is_checked = serializers.SerializerMethodField()
    packing_id = serializers.SerializerMethodField()
    item_remove_status = serializers.SerializerMethodField()

    def get_item_remove_status(self, obj):
        remove_handle = 100
        sir = ShipItemRemove.objects.filter(sku=obj.sku).filter(Q(handle=0) | Q(handle=3)).first()
        if sir:
            remove_handle = sir.handle
        return remove_handle

    def get_need_qty(self, obj):
        qty = 0
        queryset = ShipDetail.objects.filter(sku=obj.sku, ship__s_status='PREPARING')
        for i in queryset:
            qty += i.qty
        return qty

    def get_total_onway_qty(self, obj):
        qty = 0
        queryset = PurchaseManage.objects.filter(sku=obj.sku, p_status='PURCHASED')
        for i in queryset:
            qty += i.buy_qty
        return qty

    def get_total_rec_qty(self, obj):
        qty = 0
        queryset = PurchaseManage.objects.filter(sku=obj.sku).filter(Q(p_status='RECEIVED') | Q(p_status='PACKED'))
        for i in queryset:
            if i.p_status == 'RECEIVED':
                qty += i.rec_qty
            if i.p_status == 'PACKED':
                qty += i.pack_qty
        return qty

    def get_is_checked(self, obj):
        product = MLProduct.objects.filter(sku=obj.sku).first()
        return product.is_checked

    def get_packing_id(self, obj):
        product = MLProduct.objects.filter(sku=obj.sku).first()
        return product.packing_id

    class Meta:
        model = PurchaseManage
        fields = (
            'id', 'p_status', 's_type', 'create_type', 'sku', 'p_name', 'label_code', 'item_id', 'image',
            'unit_cost', 'length', 'width', 'heigth', 'weight', 'buy_qty', 'rec_qty', 'pack_qty', 'used_qty',
            'used_batch', 'from_batch', 'note', 'shop', 'shop_color', 'packing_name', 'packing_size', 'create_time',
            'buy_time', 'rec_time', 'pack_time', 'used_time', 'location', 'is_urgent', 'need_qty', 'total_onway_qty',
            'total_rec_qty', 'is_checked', 'packing_id', 'is_qc', 'item_remove_status', 'platform')


class UPCSerializer(serializers.ModelSerializer):
    """
    UPC号码池
    """
    user_name = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        return obj.user.first_name if obj.user else ''

    class Meta:
        model = UPC
        fields = ('id', 'number', 'is_used', 'user_name', 'create_time', 'use_time')


class RefillRecommendSerializer(serializers.ModelSerializer):
    """
    补货推荐
    """

    class Meta:
        model = RefillRecommend
        fields = "__all__"


class RefillSettingsSerializer(serializers.ModelSerializer):
    """
    补货推荐设置
    """

    class Meta:
        model = RefillSettings
        fields = "__all__"


class CarrierTrackSerializer(serializers.ModelSerializer):
    """
    运单物流跟踪
    """

    class Meta:
        model = CarrierTrack
        fields = "__all__"
