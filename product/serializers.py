from rest_framework import serializers

from store.models import Stock
from store.serializers import StockSerializer
from .models import Product, ProductExtraInfo, DeviceModel, CompatibleModel, ProductTag, Supplier


class ProductTagSerializer(serializers.ModelSerializer):
    """
    产品标签表
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
        model = ProductTag
        fields = ('id', 'product', 'tag', 'tag_name', 'color')


class CompatibleModelSerializer(serializers.ModelSerializer):
    """
    兼容手机型号表
    """
    phone_model = serializers.SerializerMethodField()

    # 获取手机型号
    def get_phone_model(self, obj):
        return obj.phone_model.model

    class Meta:
        model = CompatibleModel
        fields = ('id', 'product', 'phone_model')


class SimpleProductSerializer(serializers.ModelSerializer):
    """
    简易产品库
    """
    class Meta:
        model = Product
        fields = ('id', 'sku', 'p_name', 'image', 'unit_cost', 'sale_price')


class ProductSerializer(serializers.ModelSerializer):
    """
    产品库
    """

    # 兼容手机型号
    product_comp_model = CompatibleModelSerializer(many=True, required=False, read_only=True)
    # 产品标签
    product_p_tag = ProductTagSerializer(many=True, required=False, read_only=True)
    # 产品库存
    product_stock = StockSerializer(many=True, required=False, read_only=True)

    #  产品总库存
    total_qty = serializers.SerializerMethodField()
    #  产品总锁仓库存
    total_lock_qty = serializers.SerializerMethodField()

    # 计算所有仓库，门店库存之和
    def get_total_qty(self, obj):
        queryset = Stock.objects.filter(product=obj)
        if queryset:
            total = 0
            for s in queryset:
                total += s.qty
            return total
        return 0

    # 计算所有仓库，门店锁仓库存之和
    def get_total_lock_qty(self, obj):
        queryset = Stock.objects.filter(product=obj)
        if queryset:
            total = 0
            for s in queryset:
                total += s.lock_qty
            return total
        return 0

    class Meta:
        model = Product
        fields = ('id', 'sku', 'p_name', 'label_name', 'image', 'status', 'brand', 'series', 'p_type', 'unit_cost', 'sale_price',
                  'length', 'width', 'heigth', 'weight', 'url', 'is_auto_promote', 'stock_strategy', 'stock_days',
                  'alert_qty', 'alert_days', 'mini_pq', 'max_pq', 'product_comp_model', 'product_p_tag', 'note',
                  'product_stock', 'total_qty', 'total_lock_qty', 'create_time')


class ProductExtraInfoSerializer(serializers.ModelSerializer):
    """
    产品附属信息
    """

    class Meta:
        model = ProductExtraInfo
        fields = "__all__"


class DeviceModelSerializer(serializers.ModelSerializer):
    """
    市面手机型号表
    """

    class Meta:
        model = DeviceModel
        fields = "__all__"


class SupplierSerializer(serializers.ModelSerializer):
    """
    供应商
    """

    class Meta:
        model = Supplier
        fields = "__all__"