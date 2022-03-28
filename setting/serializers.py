from rest_framework import serializers
from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    """
    标签库
    """

    class Meta:
        model = Tag
        fields = "__all__"
