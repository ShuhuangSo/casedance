from django.urls import path
from feishu.views import FeishuAuthView

urlpatterns = [
    path('auth/', FeishuAuthView.as_view(), name='feishu_auth'),
]
