from rest_framework import serializers
from datetime import datetime, timedelta
from xToolkit import xstring

from mercado.models import Listing, ListingTrack, Categories, Seller, SellerTrack, MLProduct, Shop, ShopStock, Ship, \
    ShipDetail, ShipBox, Carrier, TransStock, MLSite, FBMWarehouse, MLOrder, Finance, Packing


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

    class Meta:
        model = MLProduct
        fields = "__all__"


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

    class Meta:
        model = ShopStock
        fields = "__all__"


class ShipDetailSerializer(serializers.ModelSerializer):
    """
    运单详情
    """

    class Meta:
        model = ShipDetail
        fields = "__all__"


class ShipSerializer(serializers.ModelSerializer):
    """
    头程运单
    """
    # 运单详情
    ship_shipDetail = ShipDetailSerializer(many=True, required=False, read_only=True)

    fbm_name = serializers.SerializerMethodField()
    fbm_address = serializers.SerializerMethodField()

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

    class Meta:
        model = Ship
        fields = (
            'id', 's_number', 'batch', 's_status', 'shop', 'target', 'envio_number', 'ship_type', 'shipping_fee',
            'extra_fee', 'fbm_warehouse', 'fbm_name', 'fbm_address', 'send_from', 'tag_name', 'tag_color',
            'carrier', 'end_date', 'ship_date', 'book_date', 'total_box', 'total_qty', 'weight', 'cbm',
            'note', 'create_time', 'ship_shipDetail')


class ShipBoxSerializer(serializers.ModelSerializer):
    """
    包装箱
    """

    class Meta:
        model = ShipBox
        fields = "__all__"


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

    def get_stock_days(self, obj):
        if obj.arrived_date:
            ad = str(obj.arrived_date)
            dd = datetime.strptime(ad, '%Y-%m-%d')
            delta = datetime.now() - dd
            return delta.days
        else:
            return 0

    class Meta:
        model = TransStock
        fields = (
            'id', 'listing_shop', 'sku', 'p_name', 'label_code', 'upc', 'item_id', 'image', 'qty',
            'unit_cost', 'first_ship_cost', 's_number', 'batch',
            'box_number', 'carrier_box_number', 'box_length', 'box_width', 'box_heigth', 'box_weight', 'box_cbm', 'note',
            'arrived_date', 'is_out', 'shop', 'stock_days')


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

    class Meta:
        model = MLOrder
        fields = "__all__"


class FinanceSerializer(serializers.ModelSerializer):
    """
    财务管理
    """

    class Meta:
        model = Finance
        fields = "__all__"


class PackingSerializer(serializers.ModelSerializer):
    """
    包材管理
    """

    class Meta:
        model = Packing
        fields = "__all__"