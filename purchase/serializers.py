from rest_framework import serializers

from purchase.models import PurchaseOrder, PurchaseDetail


class PurchaseDetailSerializer(serializers.ModelSerializer):
    """
    采购商品明细
    """

    class Meta:
        model = PurchaseDetail
        fields = "__all__"


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """
    采购单
    """

    #  采购商品明细
    purchase_detail = PurchaseDetailSerializer(many=True, required=False, read_only=True)

    username = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()

    # 获取username
    def get_username(self, obj):
        return obj.user.username

    # 获取收货仓库名称
    def get_store_name(self, obj):
        return obj.store.store_name

    # 获取供应商名称
    def get_supplier_name(self, obj):
        return obj.supplier.supplier_name

    class Meta:
        model = PurchaseOrder
        fields = ('id', 'p_number', 'store_name', 'supplier_name', 'username', 'logistic', 'tracking_number', 'postage',
                  'total_cost', 'total_paid', 'paid_status', 'order_status', 'note', 'purchase_detail', 'create_time',
                  'is_active')
