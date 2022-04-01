from rest_framework import serializers
from casedance.settings import BASE_URL, MEDIA_URL

from sale.models import CustomerDiscount, Customer, CustomerTag, OrderDetail, Order, OrderTag
from store.models import Stock


class CustomerTagSerializer(serializers.ModelSerializer):
    """
    客户标签
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
        model = CustomerTag
        fields = ('id', 'customer', 'tag_name', 'color')


class CustomerDiscountSerializer(serializers.ModelSerializer):
    """
    客户专属优惠
    """
    p_series = serializers.SerializerMethodField()

    # 获取系列名称
    def get_p_series(self, obj):
        return obj.p_series.name

    class Meta:
        model = CustomerDiscount
        fields = ('id', 'customer', 'p_series', 'discount_type', 'discount_money', 'discount_percent', 'create_time')


class CustomerSerializer(serializers.ModelSerializer):
    """
    客户
    """
    #  客户专属优惠
    customer_discount = CustomerDiscountSerializer(many=True, required=False, read_only=True)
    #  客户标签
    customer_tag = CustomerTagSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Customer
        fields = ('id', 'company_name', 'customer_code', 'pay_way', 'address', 'contact_name', 'phone', 'qq', 'wechat',
                  'email', 'level', 'is_active', 'note', 'customer_discount', 'customer_tag', 'create_time')


class OrderTagSerializer(serializers.ModelSerializer):
    """
    销售单标签
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
        model = OrderTag
        fields = ('id', 'order', 'tag_name', 'color')


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    销售单明细
    """
    product_image = serializers.SerializerMethodField()
    product_sku = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    p_series = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()
    stock_qty = serializers.SerializerMethodField()
    lock_qty = serializers.SerializerMethodField()
    ave_qty = serializers.SerializerMethodField()

    # # 获取产品图片
    def get_product_image(self, obj):
        return BASE_URL + MEDIA_URL + str(obj.product.image) if obj.product.image else ''

    # 获取产品sku
    def get_product_sku(self, obj):
        return obj.product.sku

    # 获取产品名称
    def get_product_name(self, obj):
        return obj.product.p_name

    # 获取产品系列名称
    def get_p_series(self, obj):
        return obj.product.series

    # 获取产品库存数量
    def get_stock_qty(self, obj):
        return Stock.objects.filter(store=obj.order.store).get(product=obj.product).qty

    # 获取产品锁定库存数量
    def get_lock_qty(self, obj):
        return Stock.objects.filter(store=obj.order.store).get(product=obj.product).lock_qty

    # 获取产品可用库存数量
    def get_ave_qty(self, obj):
        qty = Stock.objects.filter(store=obj.order.store).get(product=obj.product).qty
        lock_qty = Stock.objects.filter(store=obj.order.store).get(product=obj.product).lock_qty
        return qty - lock_qty

    # 如果结算数量大于等于发货数量，则将该项标为已结算(付款数量不等于0)
    def get_is_paid(self, obj):
        return obj.paid_qty >= obj.sent_qty if obj.paid_qty else False

    class Meta:
        model = OrderDetail
        fields = ('id', 'order', 'product_image', 'product_sku', 'product_name', 'p_series', 'qty', 'unit_price',
                  'sold_price', 'sent_qty', 'paid_qty', 'stock_qty', 'lock_qty', 'ave_qty', 'is_paid', 'create_time')


class OrderSerializer(serializers.ModelSerializer):
    """
    销售单
    """
    #  销售单明细
    order_detail = OrderDetailSerializer(many=True, required=False, read_only=True)
    #  销售单标签
    order_tag = OrderTagSerializer(many=True, required=False, read_only=True)

    username = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    total_sold_price = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    total_qty = serializers.SerializerMethodField()
    total_sent_qty = serializers.SerializerMethodField()
    total_paid_qty = serializers.SerializerMethodField()

    # 获取username
    def get_username(self, obj):
        return obj.user.first_name

    # 获取收货仓库名称
    def get_store_name(self, obj):
        return obj.store.store_name

    # 获取客户名称
    def get_customer_name(self, obj):
        return obj.customer.company_name

    # 获取销售单总金额
    def get_total_sold_price(self, obj):
        queryset = OrderDetail.objects.filter(order=obj)
        total = 0.0
        for i in queryset:
            total += i.qty*i.sold_price
        return total + obj.postage

    # 获取结算总金额
    def get_total_paid(self, obj):
        queryset = OrderDetail.objects.filter(order=obj)
        total = 0.0
        for i in queryset:
            total += i.paid_qty*i.sold_price
        return total + obj.postage if total else total

    # 获取销售单总数量
    def get_total_qty(self, obj):
        queryset = OrderDetail.objects.filter(order=obj)
        total = 0
        for i in queryset:
            total += i.qty
        return total

    # 获取已发货总数量
    def get_total_sent_qty(self, obj):
        queryset = OrderDetail.objects.filter(order=obj)
        total = 0
        for i in queryset:
            total += i.sent_qty
        return total

    # 获取已结算总数量
    def get_total_paid_qty(self, obj):
        queryset = OrderDetail.objects.filter(order=obj)
        total = 0
        for i in queryset:
            total += i.paid_qty
        return total

    class Meta:
        model = Order
        fields = ('id', 'order_number', 'store_name', 'customer_name', 'username', 'logistic', 'tracking_number', 'postage',
                  'order_type', 'order_status', 'pay_way', 'paid_status',
                  'total_sold_price', 'total_paid', 'total_qty', 'total_sent_qty', 'total_paid_qty',
                  'address', 'contact_name', 'phone', 'note', 'order_detail', 'order_tag', 'create_time', 'is_active')