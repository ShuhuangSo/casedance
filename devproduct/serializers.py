from rest_framework import serializers
from django.contrib.auth import get_user_model
from casedance.settings import BASE_URL
from devproduct.models import DevProduct, DevPrice, DevChannelData, DevListingChannel, DevListingAccount
from datetime import datetime, timedelta


class DevPriceSerializer(serializers.ModelSerializer):
    """
    产品开发定价列表
    """

    class Meta:
        model = DevPrice
        fields = "__all__"


class DevListingChannelSerializer(serializers.ModelSerializer):
    """
    开发产品发布渠道
    """

    class Meta:
        model = DevListingChannel
        fields = "__all__"


class DevListingAccountSerializer(serializers.ModelSerializer):
    """
    开发产品上架账号
    """
    # 销售链接
    sale_url = serializers.SerializerMethodField()
    # 产品图片
    image = serializers.SerializerMethodField()
    # 产品sku
    sku = serializers.SerializerMethodField()
    # 产品中文名称
    cn_name = serializers.SerializerMethodField()
    # 产品英文名称
    en_name = serializers.SerializerMethodField()
    # 产品定价
    price = serializers.SerializerMethodField()
    # 上线时间
    life_time = serializers.SerializerMethodField()

    def get_sale_url(self, obj):
        url = ''
        if obj.item_id:
            if obj.platform == 'eBay':
                if obj.site == 'AU':
                    url = 'https://www.ebay.com.au/itm/' + obj.item_id
                if obj.site == 'UK':
                    url = 'https://www.ebay.co.uk/itm/' + obj.item_id
            if obj.platform == 'MERCADO':
                url = 'https://articulo.mercadolibre.com.mx/' + obj.site + '-' + obj.item_id
            if obj.platform == 'NOON':
                url = 'https://www.noon.com/product/{item_id}/p/?o={item_id}-1'.format(
                    item_id=obj.item_id)
            if obj.platform == 'OZON':
                url = 'https://www.ozon.ru/product/{item_id}'.format(
                    item_id=obj.item_id)
        return url

    def get_image(self, obj):
        if obj.dev_p.image:
            return BASE_URL + obj.dev_p.image.url
        else:
            return ''

    def get_sku(self, obj):
        return obj.dev_p.sku

    def get_cn_name(self, obj):
        return obj.dev_p.cn_name

    def get_en_name(self, obj):
        return obj.dev_p.en_name

    def get_price(self, obj):
        dp = DevPrice.objects.filter(dev_p=obj.dev_p,
                                     platform=obj.platform,
                                     site=obj.site).first()
        if dp:
            return '{currency} {price}'.format(currency=dp.currency,
                                               price=dp.price)
        else:
            return 0

    def get_life_time(self, obj):
        life_time = ''
        if obj.is_online:
            # 天数
            days = (datetime.now() - obj.online_time).days
            hours = round((datetime.now() - obj.online_time).seconds / 3600, 1)
            if days > 0:
                life_time = '{day} 天'.format(day=days)
            else:
                life_time = '{hour} 小时'.format(hour=hours)
        return life_time

    class Meta:
        model = DevListingAccount
        fields = ('id', 'dev_p', 'platform', 'site', 'account_name', 'user_id',
                  'user_name', 'item_id', 'is_online', 'online_time',
                  'offline_time', 'note', 'sale_url', 'notify', 'is_paused',
                  'image', 'sku', 'cn_name', 'en_name', 'price', 'create_time',
                  'life_time')


class DevProductSerializer(serializers.ModelSerializer):
    """
    产品开发列表
    """
    # 产品开发定价列表
    dev_price = DevPriceSerializer(many=True, required=False, read_only=True)
    # 开发产品发布渠道
    dev_listing_channel = DevListingChannelSerializer(many=True,
                                                      required=False,
                                                      read_only=True)
    # 开发产品上架账号
    # dev_listing_account = DevListingAccountSerializer(many=True,
    #                                                   required=False,
    #                                                   read_only=True)
    # 关联数量
    cp_count = serializers.SerializerMethodField()
    # 通知信息确认
    notify = serializers.SerializerMethodField()
    # 创建人名称
    user_name = serializers.SerializerMethodField()

    def get_cp_count(self, obj):
        if obj.cp_id:
            return DevProduct.objects.filter(cp_id=obj.cp_id).count()
        else:
            return 0

    def get_notify(self, obj):
        dla_list = DevListingAccount.objects.filter(dev_p=obj)
        for i in dla_list:
            if i.notify:
                return True
        return False

    def get_user_name(self, obj):
        User = get_user_model()
        user = User.objects.filter(id=obj.user_id).first()
        return user.first_name if user else 'System'

    class Meta:
        model = DevProduct
        fields = ('id', 'sku', 'cn_name', 'en_name', 'image', 'is_elec',
                  'is_magnet', 'is_water', 'is_dust', 'is_confirm_data',
                  'is_stock', 'keywords', 'category', 'package_included',
                  'unit_cost', 'p_length', 'p_width', 'p_height', 'p_weight',
                  'buy_url1', 'buy_url2', 'buy_url3', 'buy_url4', 'buy_url5',
                  'refer_url1', 'refer_url2', 'desc', 'note', 'create_time',
                  'online_time', 'offline_time', 'user_id', 'qty', 'percent',
                  'rate', 'p_status', 'buy_status', 'tag_name', 'tag_color',
                  'dev_price', 'dev_listing_channel', 'cp_id', 'cp_count',
                  'notify', 'user_name', 'local_category')


class DevChannelDataSerializer(serializers.ModelSerializer):
    """
    开发平台渠道数据
    """

    class Meta:
        model = DevChannelData
        fields = "__all__"
