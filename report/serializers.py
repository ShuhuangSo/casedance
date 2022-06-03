from rest_framework import serializers

from report.models import SalesReport, StockReport, CustomerReport


class SalesReportSerializer(serializers.ModelSerializer):
    """
    销量统计
    """

    class Meta:
        model = SalesReport
        fields = ('id', 'amount', 'series', 'sale_date', 'qty')


class StockReportSerializer(serializers.ModelSerializer):
    """
    库存统计
    """

    class Meta:
        model = StockReport
        fields = ('id', 'amount', 'series', 'stock_date', 'qty')


class CustomerReportSerializer(serializers.ModelSerializer):
    """
    客户销量统计报告
    """
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.customer.company_name

    class Meta:
        model = CustomerReport
        fields = ('id', 'amount', 'series', 'calc_date', 'qty', 'name')