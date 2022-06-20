from rest_framework import serializers

from bonus.models import AccountSales, AccountBonus, Accounts, MonthList, ExchangeRate, BasicInfo


class AccountSalesSerializer(serializers.ModelSerializer):
    """
    账号销售报表
    """

    class Meta:
        model = AccountSales
        fields = "__all__"
        depth = 2


class AccountBonusSerializer(serializers.ModelSerializer):
    """
    提成表
    """

    class Meta:
        model = AccountBonus
        fields = "__all__"


class AccountsSerializer(serializers.ModelSerializer):
    """
    账号
    """

    class Meta:
        model = Accounts
        fields = "__all__"
        depth = 2


class MonthListSerializer(serializers.ModelSerializer):
    """
    统计月份
    """

    class Meta:
        model = MonthList
        fields = "__all__"


class ExchangeRateSerializer(serializers.ModelSerializer):
    """
    汇率
    """

    class Meta:
        model = ExchangeRate
        fields = "__all__"


class BasicInfoSerializer(serializers.ModelSerializer):
    """
    基础信息
    """

    class Meta:
        model = BasicInfo
        fields = "__all__"