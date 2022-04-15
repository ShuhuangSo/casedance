from rest_framework import serializers
from casedance.settings import BASE_URL, MEDIA_URL

from sale.models import Order
from .models import Store, Stock, StockInOut, StockInOutDetail, StockLog


class StoreSerializer(serializers.ModelSerializer):
    """
    仓库、销售门店
    """

    class Meta:
        model = Store
        fields = "__all__"


class StockSerializer(serializers.ModelSerializer):
    """
    产品库存
    """
    store_name = serializers.SerializerMethodField()

    # 获取门店名称
    def get_store_name(self, obj):
        return obj.store.store_name

    class Meta:
        model = Stock
        fields = ('id', 'qty', 'lock_qty', 'product', 'store_name', 'avg_sales', 'recent_7d_sales', 'recent_30d_sales',
                  'last_sale_time')


class StockInOutDetailSerializer(serializers.ModelSerializer):
    """
    出入库产品明细
    """
    sku = serializers.SerializerMethodField()
    p_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    # 获取sku
    def get_sku(self, obj):
        return obj.product.sku

    # 获取产品名称
    def get_p_name(self, obj):
        return obj.product.p_name

    # 获取产品image
    def get_image(self, obj):
        return BASE_URL + MEDIA_URL + str(obj.product.image) if obj.product.image else ''

    class Meta:
        model = StockInOutDetail
        fields = ('id', 'qty', 'stock_before', 'sku', 'p_name', 'image')


class StockInOutSerializer(serializers.ModelSerializer):
    """
    手工出入库/调拨
    """

    #  出入库产品明细
    inout_detail = StockInOutDetailSerializer(many=True, required=False, read_only=True)

    username = serializers.SerializerMethodField()
    origin_store_name = serializers.SerializerMethodField()
    target_store_name = serializers.SerializerMethodField()
    sku_num = serializers.SerializerMethodField()

    # 获取username
    def get_username(self, obj):
        return obj.user.first_name

    # 获取sku数
    def get_sku_num(self, obj):
        return obj.inout_detail.count()

    # 获取源仓库名称
    def get_origin_store_name(self, obj):
        return obj.origin_store.store_name

    # 获取目标仓库名称
    def get_target_store_name(self, obj):
        return obj.target_store.store_name

    class Meta:
        model = StockInOut
        fields = ('id', 'batch_number', 'origin_store', 'origin_store_name', 'target_store', 'target_store_name', 'username', 'type', 'reason_in', 'reason_out',
                  'reason_move', 'inout_detail', 'sku_num', 'note', 'create_time', 'is_active')


class StockLogSerializer(serializers.ModelSerializer):
    """
    库存出入日志
    """

    #  出入库产品明细
    # inout_detail = StockInOutDetailSerializer(many=True, required=False, read_only=True)
    #
    username = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    op_batch_number = serializers.SerializerMethodField()

    # 获取username
    def get_username(self, obj):
        return obj.user.first_name

    # # 获取源仓库名称
    def get_store_name(self, obj):
        return obj.store.store_name
    #
    # # 获取源操作单批次号
    def get_op_batch_number(self, obj):
        if obj.op_type in ['M_IN', 'M_OUT']:
            number = StockInOut.objects.get(id=obj.op_origin_id).batch_number
        if obj.op_type in ['S_OUT', 'LOCK', 'UNLOCK']:
            number = Order.objects.get(id=obj.op_origin_id).order_number
        return number

    class Meta:
        model = StockLog
        fields = ('id', 'op_type', 'op_origin_id', 'op_batch_number', 'qty', 'username', 'store_name', 'product', 'create_time')
