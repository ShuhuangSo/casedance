from rest_framework import serializers
from .models import Store, Stock


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
