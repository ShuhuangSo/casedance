"""
飞书 API 封装 — 供免登和通知共用。

FeishuAPI 单次实例化即自动管理 tenant_access_token：
  - 首次获取后缓存到 Redis，110 分钟后过期（飞书有效期 2 小时）
  - 后续调用直接从 Redis 读取，避免频繁请求飞书
"""
import json
import time
import requests
import redis
from django.conf import settings


class FeishuAPI:
    """飞书开放平台 API 封装"""

    BASE_URL = 'https://open.feishu.cn/open-apis'
    REDIS_KEY = 'feishu:tenant_access_token'

    def __init__(self):
        self.app_id = settings.FEISHU_APP_ID
        self.app_secret = settings.FEISHU_APP_SECRET
        self._redis = None

    @property
    def redis(self):
        if self._redis is None:
            self._redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=getattr(settings, 'REDIS_DB', 1),
                decode_responses=True)
        return self._redis

    # ---------- Tenant Access Token ----------

    def get_tenant_access_token(self) -> str:
        """获取 tenant_access_token（优先从 Redis 缓存读取）"""
        cached = self.redis.get(self.REDIS_KEY)
        if cached:
            return cached.strip('"')

        token, expires = self._fetch_tenant_access_token()
        self.redis.setex(self.REDIS_KEY, expires - 60, token)
        return token

    def _fetch_tenant_access_token(self) -> tuple:
        """请求飞书获取新的 tenant_access_token，返回 (token, expires_in)"""
        resp = requests.post(
            f'{self.BASE_URL}/auth/v3/tenant_access_token/internal',
            json={'app_id': self.app_id, 'app_secret': self.app_secret},
            timeout=10)
        data = resp.json()
        if data.get('code') != 0:
            raise Exception(f'获取 tenant_access_token 失败: {data}')
        return data['tenant_access_token'], data.get('expire', 7200)

    # ---------- 免登 ----------

    @staticmethod
    def exchange_code(code: str) -> dict:
        """免登 code 换取 user_access_token 和 open_id。
        返回: {"open_id": "xxx", "access_token": "xxx", "name": "xxx"} 或 None
        """
        resp = requests.post(
            f'{FeishuAPI.BASE_URL}/authen/v1/access_token',
            headers={'Content-Type': 'application/json'},
            json={'grant_type': 'authorization_code', 'code': code},
            timeout=10)
        data = resp.json()
        if data.get('code') != 0:
            return None
        return data.get('data')

    def get_user_mobile(self, open_id: str, user_access_token: str = None) -> str:
        """获取飞书用户手机号（国际化格式如 "86-13800138000"）。
        返回纯手机号（去前缀），失败返回空字符串。

        飞书用户信息接口支持两种鉴权：
        - 免登场景：传 user_access_token（从 exchange_code 返回）
        - Bot 场景：不传，用 tenant_access_token 请求通讯录接口（需授权）
        """
        if user_access_token:
            resp = requests.get(
                f'{self.BASE_URL}/authen/v1/user_info',
                headers={
                    'Authorization': f'Bearer {user_access_token}',
                    'Content-Type': 'application/json',
                },
                timeout=10)
        else:
            tenant_token = self.get_tenant_access_token()
            resp = requests.get(
                f'{self.BASE_URL}/contact/v3/users/{open_id}',
                headers={'Authorization': f'Bearer {tenant_token}'},
                timeout=10)
        data = resp.json()
        if data.get('code') != 0:
            return ''

        if user_access_token:
            mobile = data.get('data', {}).get('mobile', '')
        else:
            mobile_list = data.get('data', {}).get('user', {}).get('mobile', '')
            mobile = mobile_list if isinstance(mobile_list, str) else ''

        # 去掉国家码前缀（如 "86-13800138000" → "13800138000"）
        if '-' in mobile:
            mobile = mobile.split('-', 1)[-1]
        return mobile

    # ---------- 消息通知（预留） ----------

    def send_message(self, open_id: str, content: dict) -> bool:
        """发送消息给指定用户。
        content 为飞书消息体，需包含 msg_type 和 content 字段。
        参考: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
        """
        token = self.get_tenant_access_token()
        body = {'receive_id': open_id, **content}
        resp = requests.post(
            f'{self.BASE_URL}/im/v1/messages?receive_id_type=open_id',
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            },
            json=body,
            timeout=10)
        data = resp.json()
        if data.get('code') != 0:
            print(f'[Feishu] send_message failed: {data}')
            return False
        return True

    def send_text(self, open_id: str, text: str) -> bool:
        """发送文本消息（便捷方法）"""
        return self.send_message(open_id, {
            'msg_type': 'text',
            'content': json.dumps({'text': text}),
        })

    def send_card(self, open_id: str, header: str, body: str,
                  url: str = None) -> bool:
        """发送卡片消息（便捷方法）"""
        card = {
            'header': {
                'title': {'tag': 'plain_text', 'content': header},
                'template': 'blue',
            },
            'elements': [{'tag': 'div', 'text': {'tag': 'plain_text', 'content': body}}],
        }
        if url:
            card['elements'].append({
                'tag': 'action',
                'actions': [{'tag': 'button', 'text': {'tag': 'plain_text', 'content': '查看详情'}, 'url': url}],
            })
        return self.send_message(open_id, {
            'msg_type': 'interactive',
            'content': json.dumps({'config': {'wide_screen_mode': True}, **card}),
        })
