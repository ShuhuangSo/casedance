from rest_framework import serializers

from casedance.settings import BASE_URL, MEDIA_URL
from purchase.models import PurchaseOrder, PurchaseDetail


class PurchaseDetailSerializer(serializers.ModelSerializer):
    """
    采购商品明细
    """
    product_image = serializers.SerializerMethodField()
    product_sku = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()

    # # 获取产品图片
    def get_product_image(self, obj):
        return BASE_URL + MEDIA_URL + str(obj.product.image) if obj.product.image else ''

    # 获取产品sku
    def get_product_sku(self, obj):
        return obj.product.sku

    # 获取产品名称
    def get_product_name(self, obj):
        return obj.product.p_name

    # 如果结算数量大于等于采购数量，则将该项标为已结算
    def get_is_paid(self, obj):
        return obj.paid_qty >= obj.qty

    class Meta:
        model = PurchaseDetail
        fields = ('id', 'qty', 'unit_cost', 'received_qty', 'paid_qty', 'is_paid', 'short_note', 'stock_before', 'product_image',
                  'product_sku', 'product_name')


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """
    采购单
    """

    #  采购商品明细
    purchase_detail = PurchaseDetailSerializer(many=True, required=False, read_only=True)

    username = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    paid_status = serializers.SerializerMethodField()

    # 获取username
    def get_username(self, obj):
        return obj.user.username

    # 获取收货仓库名称
    def get_store_name(self, obj):
        return obj.store.store_name

    # 获取供应商名称
    def get_supplier_name(self, obj):
        return obj.supplier.supplier_name

    # 获取采购单总金额
    def get_total_cost(self, obj):
        queryset = PurchaseDetail.objects.filter(purchase_order=obj)
        total = 0.0
        for i in queryset:
            total += i.qty*i.unit_cost
        return total + obj.postage

    # 获取结算总金额
    def get_total_paid(self, obj):
        queryset = PurchaseDetail.objects.filter(purchase_order=obj)
        total = 0.0
        for i in queryset:
            total += i.paid_qty*i.unit_cost
        return total + obj.postage

    # 获取采购单结算状态
    def get_paid_status(self, obj):
        queryset = PurchaseDetail.objects.filter(purchase_order=obj)
        count = PurchaseDetail.objects.filter(purchase_order=obj).count()
        num = 0
        status = 'UNPAID'
        for i in queryset:
            if i.paid_qty >= i.qty:
                num += 1
        if num == count:
            status = 'FULL_PAID'
        elif 0 < num < count:
            status = 'PART_PAID'
        return status

    class Meta:
        model = PurchaseOrder
        fields = ('id', 'p_number', 'store_name', 'supplier_name', 'username', 'logistic', 'tracking_number', 'postage',
                  'total_cost', 'total_paid', 'paid_status', 'order_status', 'note', 'purchase_detail', 'create_time',
                  'is_active')
