from rest_framework import serializers
from django.db.models import Q, Sum
from datetime import datetime

from purchase.models import PurchaseDetail
from store.models import Stock
from store.serializers import StockSerializer
from .models import Product, ProductExtraInfo, DeviceModel, CompatibleModel, ProductTag, Supplier, DeviceBrand


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
        fields = ('id', 'sku', 'p_name', 'series', 'image', 'unit_cost', 'sale_price')


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
    #  正在采购数量
    purchase_qty = serializers.SerializerMethodField()
    #  在途数量
    on_way_qty = serializers.SerializerMethodField()

    # 计算正在采购数量之和
    def get_purchase_qty(self, obj):

        q = Q()
        q.connector = 'OR'
        q.children.append(('purchase_order__order_status', 'WAIT_CONFIRM'))
        q.children.append(('purchase_order__order_status', 'IN_PRODUCTION'))
        q.children.append(('purchase_order__order_status', 'PART_SENT'))
        q.children.append(('purchase_order__order_status', 'SENT'))
        # 计算正在采购的数量,状态为 WAIT_CONFIRM，IN_PRODUCTION，SENT, PART_SENT采购单中的下单数量 QTY
        sum_qty = PurchaseDetail.objects.filter(product=obj).filter(q).aggregate(Sum('qty'))
        buy_qty = 0
        if sum_qty['qty__sum']:
            buy_qty = sum_qty['qty__sum']

        return buy_qty

    # 计算在途数量之和
    def get_on_way_qty(self, obj):

        q = Q()
        q.connector = 'OR'
        q.children.append(('purchase_order__order_status', 'PART_SENT'))
        q.children.append(('purchase_order__order_status', 'SENT'))
        # 计算正在采购的在途数量,状态为SENT, PART_SENT采购单中的发货数量 sent_qty - 收货数量received_qty
        sum_sent = PurchaseDetail.objects.filter(product=obj).filter(q).aggregate(Sum('sent_qty'))
        sum_rec = PurchaseDetail.objects.filter(product=obj).filter(q).aggregate(Sum('received_qty'))

        if sum_sent['sent_qty__sum']:
            rec1 = sum_sent['sent_qty__sum']
        else:
            rec1 = 0
        if sum_rec['received_qty__sum']:
            rec2 = sum_rec['received_qty__sum']
        else:
            rec2 = 0
        on_way_qty = rec1 - rec2

        return on_way_qty

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
                  'product_stock', 'total_qty', 'total_lock_qty', 'purchase_qty', 'on_way_qty', 'create_time')


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
    cp_model = serializers.SerializerMethodField()
    is_new = serializers.SerializerMethodField()

    # 获取兼容设备型号
    def get_cp_model(self, obj):
        if obj.cp_id:
            add_list = []
            queryset = DeviceModel.objects.filter(cp_id=obj.cp_id)
            for i in queryset:
                if i.model != obj.model:
                    add_list.append({'model': i.model})
            return add_list
        return []

    def get_is_new(self, obj):
        d = datetime.now().date() - obj.create_time.date()
        if d.days < 10:
            return True
        return False

    class Meta:
        model = DeviceModel
        fields = ('id', 'brand', 'type', 'model', 'cp_id', 'cp_model', 'note', 'image', 'dimensions', 'weight', 'link',
                  'announced', 'status', 'detail_model', 'create_time', 'is_new')


class SupplierSerializer(serializers.ModelSerializer):
    """
    供应商
    """

    class Meta:
        model = Supplier
        fields = "__all__"


class DeviceBrandSerializer(serializers.ModelSerializer):
    """
    市面手机品牌
    """

    class Meta:
        model = DeviceBrand
        fields = "__all__"