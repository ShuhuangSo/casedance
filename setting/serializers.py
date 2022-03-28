from rest_framework import serializers
from .models import Tag, OperateLog


class TagSerializer(serializers.ModelSerializer):
    """
    标签库
    """

    class Meta:
        model = Tag
        fields = "__all__"


class OperateLogSerializer(serializers.ModelSerializer):
    """
    操作日志
    """

    class Meta:
        model = OperateLog
        fields = "__all__"
