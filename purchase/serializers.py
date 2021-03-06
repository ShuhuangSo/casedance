from rest_framework import serializers
from django.db.models import Sum

from casedance.settings import BASE_URL, MEDIA_URL
from purchase.models import PurchaseOrder, PurchaseDetail, PurchaseOrderTag, PostInfo, RefillPromote
from store.models import Stock


class PurchaseOrderTagSerializer(serializers.ModelSerializer):
    """
    采购单标签表
    """
    tag_name = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    # 获取标签名
    def get_tag_name(self, obj):
        return obj.tag.tag_name

    # 获取颜色
    def get_color(self, obj):
        return obj.tag.color

    class Meta:
        model = PurchaseOrderTag
        fields = ('id', 'purchase_order', 'tag', 'tag_name', 'color')


class PurchaseDetailSerializer(serializers.ModelSerializer):
    """
    采购商品明细
    """
    image = serializers.SerializerMethodField()
    sku = serializers.SerializerMethodField()
    p_name = serializers.SerializerMethodField()
    # is_paid = serializers.SerializerMethodField()
    onway_qty = serializers.SerializerMethodField()

    #  产品总库存
    total_qty = serializers.SerializerMethodField()
    #  产品总锁仓库存
    total_lock_qty = serializers.SerializerMethodField()
    ava_qty = serializers.SerializerMethodField()

    # 计算所有仓库，门店库存之和
    def get_total_qty(self, obj):
        queryset = Stock.objects.filter(product=obj.product)
        if queryset:
            total = 0
            for s in queryset:
                total += s.qty
            return total
        return 0

    # 计算所有仓库，门店锁仓库存之和
    def get_total_lock_qty(self, obj):
        queryset = Stock.objects.filter(product=obj.product)
        if queryset:
            total = 0
            for s in queryset:
                total += s.lock_qty
            return total
        return 0

    def get_ava_qty(self, obj):
        queryset = Stock.objects.filter(product=obj.product)
        if queryset:
            total = 0
            lock = 0
            for s in queryset:
                total += s.qty
                lock += s.lock_qty
            return total - lock
        return 0

    # # 获取产品图片
    def get_image(self, obj):
        return BASE_URL + MEDIA_URL + str(obj.product.image) if obj.product.image else ''

    # 获取产品sku
    def get_sku(self, obj):
        return obj.product.sku

    # 获取产品名称
    def get_p_name(self, obj):
        return obj.product.p_name

    # 如果结算数量大于等于收货数量，则将该项标为已结算(付款数量不等于0)
    # def get_is_paid(self, obj):
    #     return obj.paid_qty >= obj.received_qty if obj.paid_qty else False

    # 获取在途数量
    def get_onway_qty(self, obj):
        return obj.sent_qty - obj.received_qty

    class Meta:
        model = PurchaseDetail
        fields = (
        'id', 'urgent', 'total_qty', 'total_lock_qty', 'ava_qty', 'qty', 'unit_cost', 'received_qty', 'paid_qty',
        'sent_qty', 'onway_qty', 'is_supply_case', 'is_paid', 'short_note', 'stock_before', 'image', 'sku', 'p_name')


class PostInfoSerializer(serializers.ModelSerializer):
    """
    采购发货物流信息
    """

    class Meta:
        model = PostInfo
        fields = "__all__"


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """
    采购单
    """

    #  采购商品明细
    purchase_detail = PurchaseDetailSerializer(many=True, required=False, read_only=True)
    #  采购单标签
    purchase_p_tag = PurchaseOrderTagSerializer(many=True, required=False, read_only=True)
    #  发货物流信息
    purchase_post_info = PostInfoSerializer(many=True, required=False, read_only=True)

    username = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    supplier_name = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    total_buy_qty = serializers.SerializerMethodField()
    total_onway_qty = serializers.SerializerMethodField()
    total_rec_qty = serializers.SerializerMethodField()
    total_paid_qty = serializers.SerializerMethodField()

    # paid_status = serializers.SerializerMethodField()

    # 获取username
    def get_username(self, obj):
        return obj.user.first_name

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
            total += i.qty * i.unit_cost
        return total + obj.postage

    # 获取结算总金额
    def get_total_paid(self, obj):
        queryset = PurchaseDetail.objects.filter(purchase_order=obj)
        total = 0.0
        for i in queryset:
            total += i.paid_qty * i.unit_cost
        return total + obj.postage if total else total

    # 获取采购总数量
    def get_total_buy_qty(self, obj):
        queryset = PurchaseDetail.objects.filter(purchase_order=obj)
        total = 0
        for i in queryset:
            total += i.qty
        return total

    # 获取在途总数量
    def get_total_onway_qty(self, obj):
        queryset = PurchaseDetail.objects.filter(purchase_order=obj)
        total = 0
        for i in queryset:
            total += i.sent_qty - i.received_qty
        return total

    # 获取已收货总数量
    def get_total_rec_qty(self, obj):
        queryset = PurchaseDetail.objects.filter(purchase_order=obj)
        total = 0
        for i in queryset:
            total += i.received_qty
        return total

    # 获取已结算总数量
    def get_total_paid_qty(self, obj):
        queryset = PurchaseDetail.objects.filter(purchase_order=obj)
        total = 0
        for i in queryset:
            total += i.paid_qty
        return total

    class Meta:
        model = PurchaseOrder
        fields = ('id', 'p_number', 'store', 'store_name', 'supplier', 'supplier_name', 'username', 'postage',
                  'inner_case_price', 'rec_name', 'rec_phone', 'rec_address', 'purchase_post_info',
                  'sup_tips', 'total_cost', 'total_paid', 'total_buy_qty', 'total_onway_qty',
                  'total_rec_qty', 'total_paid_qty', 'paid_status', 'order_status', 'note', 'purchase_detail',
                  'purchase_p_tag', 'create_time', 'is_active')


class RefillPromoteSerializer(serializers.ModelSerializer):
    """
    智能补货推荐
    """
    sku = serializers.SerializerMethodField()
    p_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    unit_cost = serializers.SerializerMethodField()
    #  产品总库存
    total_qty = serializers.SerializerMethodField()
    #  产品总锁仓库存
    total_lock_qty = serializers.SerializerMethodField()
    #  产品7天总销量
    total_7d_sold = serializers.SerializerMethodField()
    #  产品30天总销量
    total_30d_sold = serializers.SerializerMethodField()

    # # 获取产品图片
    def get_image(self, obj):
        return BASE_URL + MEDIA_URL + str(obj.product.image) if obj.product.image else ''
    # 计算所有仓库，门店库存之和
    def get_total_qty(self, obj):
        sum_stock = Stock.objects.filter(product=obj.product).aggregate(Sum('qty'))
        return sum_stock['qty__sum']

    # 计算所有仓库，门店锁仓库存之和
    def get_total_lock_qty(self, obj):
        sum_lock = Stock.objects.filter(product=obj.product).aggregate(Sum('lock_qty'))
        return sum_lock['lock_qty__sum']

    # 计算所有仓库，门店产品7天总销量
    def get_total_7d_sold(self, obj):
        sum_7d = Stock.objects.filter(product=obj.product).aggregate(Sum('recent_7d_sales'))
        return sum_7d['recent_7d_sales__sum']

    # 计算所有仓库，门店产品30天总销量
    def get_total_30d_sold(self, obj):
        sum_30d = Stock.objects.filter(product=obj.product).aggregate(Sum('recent_30d_sales'))
        return sum_30d['recent_30d_sales__sum']

    def get_sku(self, obj):
        return obj.product.sku

    def get_p_name(self, obj):
        return obj.product.p_name

    def get_unit_cost(self, obj):
        return obj.product.unit_cost

    class Meta:
        model = RefillPromote
        fields = ('id', 'qty', 'product', 'sku', 'image', 'p_name', 'unit_cost', 'total_qty', 'total_lock_qty', 'total_7d_sold',
                  'create_time', 'total_30d_sold')
