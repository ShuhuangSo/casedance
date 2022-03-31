from rest_framework import serializers

from sale.models import CustomerDiscount, Customer, CustomerTag


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
                  'email', 'is_active', 'note', 'customer_discount', 'customer_tag', 'create_time')