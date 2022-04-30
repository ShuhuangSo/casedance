from rest_framework import serializers
from .models import Tag, OperateLog, Menu
from django.contrib.auth import get_user_model

User = get_user_model()


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
    user_name = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        return obj.user.first_name

    class Meta:
        model = OperateLog
        fields = ('id', 'op_type', 'op_log', 'target_id', 'create_time', 'user_name')


class SubMenuSerializer(serializers.ModelSerializer):
    """
    前端导航二级菜单
    """

    class Meta:
        model = Menu
        fields = ('id', 'parent', 'path', 'component', 'name', 'icon', 'order_num', 'is_active', 'children')


class MenuSerializer(serializers.ModelSerializer):
    """
    前端导航菜单
    """
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        user = self.context['request'].user  # 当前登录u用户
        # 返回嵌套序列化筛选数据
        return SubMenuSerializer(obj.children.filter(is_active=True, user=user), many=True).data

    class Meta:
        model = Menu
        fields = ('id', 'parent', 'path', 'component', 'name', 'icon', 'order_num', 'is_active', 'children', 'user')


class ALLMenuSerializer(serializers.ModelSerializer):
    """
    前端导航菜单
    """
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        user = User.objects.get(username='admin')  # admin用户
        # 返回嵌套序列化筛选数据
        return SubMenuSerializer(obj.children.filter(user=user), many=True).data

    class Meta:
        model = Menu
        fields = ('id', 'parent', 'path', 'component', 'name', 'icon', 'order_num', 'is_active', 'children', 'user')


class UserMenuSerializer(serializers.ModelSerializer):
    """
    前端导航菜单
    """
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        id = self.context['request'].GET.get("id")
        user = User.objects.get(id=id)
        # 返回嵌套序列化筛选数据
        return SubMenuSerializer(obj.children.filter(user=user), many=True).data

    class Meta:
        model = Menu
        fields = ('id', 'parent', 'path', 'component', 'name', 'icon', 'order_num', 'is_active', 'children', 'user')


class UserSerializer(serializers.ModelSerializer):
    """
    用户信息
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined',
                  'is_superuser', 'last_login')
