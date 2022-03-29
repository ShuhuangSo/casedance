from rest_framework import serializers
from .models import Store, Stock, StockInOut, StockInOutDetail


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

    class Meta:
        model = StockInOutDetail
        fields = "__all__"


class StockInOutSerializer(serializers.ModelSerializer):
    """
    手工出入库/调拨
    """

    #  出入库产品明细
    inout_detail = StockInOutDetailSerializer(many=True, required=False, read_only=True)

    username = serializers.SerializerMethodField()
    origin_store_name = serializers.SerializerMethodField()
    target_store_name = serializers.SerializerMethodField()

    # 获取username
    def get_username(self, obj):
        return obj.user.username

    # 获取源仓库名称
    def get_origin_store_name(self, obj):
        return obj.origin_store.store_name

    # 获取目标仓库名称
    def get_target_store_name(self, obj):
        return obj.target_store.store_name

    class Meta:
        model = StockInOut
        fields = ('id', 'batch_number', 'origin_store_name', 'target_store_name', 'username', 'type', 'reason_in', 'reason_out',
                  'reason_move', 'inout_detail', 'create_time', 'is_active')
