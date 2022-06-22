from rest_framework import serializers

from bonus.models import AccountSales, AccountBonus, Accounts, MonthList, ExchangeRate, BasicInfo, Manager


class AccountSalesSerializer(serializers.ModelSerializer):
    """
    账号销售报表
    """

    class Meta:
        model = AccountSales
        fields = "__all__"
        depth = 1


class AccountSalesSerializerNodepth(serializers.ModelSerializer):
    """
    No depth账号销售报表
    """

    class Meta:
        model = AccountSales
        fields = "__all__"


class AccountBonusSerializer(serializers.ModelSerializer):
    """
    提成表
    """

    class Meta:
        model = AccountBonus
        fields = "__all__"
        depth = 1


class AccountsSerializer(serializers.ModelSerializer):
    """
    账号
    """

    class Meta:
        model = Accounts
        fields = "__all__"
        depth = 1


class AccountsSerializerNodepth(serializers.ModelSerializer):
    """
    no depth账号
    """

    class Meta:
        model = Accounts
        fields = "__all__"


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


class ManagerSerializer(serializers.ModelSerializer):
    """
    运营负责人
    """

    class Meta:
        model = Manager
        fields = "__all__"