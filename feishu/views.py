"""
飞书集成 Views
- FeishuAuthView: 免登接口 POST /api/feishu/auth/
"""
import time
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.utils import jwt_payload_handler, jwt_encode_handler

from feishu.api import FeishuAPI
from feishu.models import FeishuUserBinding


class FeishuAuthView(APIView):
    """飞书免登接口"""
    authentication_classes = []  # 免登接口无需鉴权
    permission_classes = []

    def post(self, request):
        code = request.data.get('code', '').strip()
        if not code:
            return Response({
                'msg': '缺少授权码 code',
                'code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)

        # 1. code 换取 open_id + user_access_token
        data = FeishuAPI.exchange_code(code)
        if not data:
            return Response({
                'msg': '飞书授权码无效或已过期',
                'code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)

        open_id = data.get('open_id', '')
        user_access_token = data.get('access_token', '')

        # 2. 检查是否已有绑定
        binding = FeishuUserBinding.objects.filter(open_id=open_id).first()
        if binding:
            user = binding.user
        else:
            # 3. 首次登录：获取手机号匹配系统用户
            api = FeishuAPI()
            mobile = api.get_user_mobile(open_id, user_access_token)
            if not mobile:
                return Response({
                    'msg': '未能获取飞书用户手机号，请确认飞书应用已配置通讯录权限',
                    'code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.filter(username=mobile).first()
            if not user:
                return Response({
                    'msg': f'手机号 {mobile} 未关联系统用户，请联系管理员',
                    'code': 403,
                }, status=status.HTTP_403_FORBIDDEN)

            # 4. 创建绑定
            FeishuUserBinding.objects.create(
                open_id=open_id, user=user, mobile=mobile)

        # 5. 签发 JWT（复用与 api-token-auth/ 一致的算法）
        payload = jwt_payload_handler(user)
        payload['orig_iat'] = int(time.time())
        token = jwt_encode_handler(payload)

        return Response({
            'token': token,
            'username': user.username,
            'name': user.first_name or user.username,
            'code': 100,
        })
