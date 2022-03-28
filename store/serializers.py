from rest_framework import serializers
from .models import Store


class StoreSerializer(serializers.ModelSerializer):
    """
    仓库、销售门店
    """

    class Meta:
        model = Store
        fields = "__all__"