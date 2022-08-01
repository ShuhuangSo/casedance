from rest_framework import serializers
from datetime import datetime, timedelta
from xToolkit import xstring

from mercado.models import Listing, ListingTrack, Categories, Seller


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

        p = n * 100 if m == 0 else int((n - m)/m * 100)
        return p

    # 获取上一个7天销量
    def get_sold_7d_grow(self, obj):
        start_date = datetime.now().date() - timedelta(days=7)
        last_start_date = start_date - timedelta(days=7)
        lt = ListingTrack.objects.filter(create_time__date__gte=start_date, listing=obj)
        n = 0
        for i in lt:
            n += i.today_sold

        lt2 = ListingTrack.objects.filter(create_time__date__gte=last_start_date, create_time__date__lt=start_date, listing=obj)
        m = 0
        for i in lt2:
            m += i.today_sold

        p = n * 100 if m == 0 else int((n - m)/m * 100)
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

        lt2 = ListingTrack.objects.filter(create_time__date__gte=last_start_date, create_time__date__lt=start_date, listing=obj)
        m = 0
        for i in lt2:
            m += i.today_sold

        p = n * 100 if m == 0 else int((n - m)/m * 100)
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

    class Meta:
        model = Seller
        fields = "__all__"