"""
图片托管服务抽象层。
当前实现：聚合图床（SuperBed）。
切换服务商只需修改此文件，无需改动业务代码。

统一接口：
    upload_by_url(image_url) -> new_url | None
"""

import time
from typing import Optional
import requests
from django.conf import settings


class ImageHostingService:
    """图片托管服务基类"""

    def upload_by_url(self, image_url: str, max_retries: int = 3) -> Optional[str]:
        """通过 URL 上传，成功返回新 URL，失败返回 None"""
        raise NotImplementedError

    def upload_file(self, file_data: bytes,
                    filename: str = None,
                    max_retries: int = 3) -> Optional[str]:
        """通过文件上传，成功返回新 URL，失败返回 None"""
        raise NotImplementedError


class SuperBedService(ImageHostingService):
    """聚合图床（SuperBed）实现"""

    def __init__(self, token: str, upload_url: str = None):
        self.token = token
        self.upload_url = upload_url or 'https://www.superbed.cc/upload'

    def upload_by_url(self, image_url: str, max_retries: int = 3) -> Optional[str]:
        for attempt in range(1, max_retries + 1):
            try:
                resp = requests.post(self.upload_url,
                                     data={
                                         'token': self.token,
                                         'src': image_url
                                     },
                                     timeout=60)
                result = resp.json()
                if result.get('err') == 0:
                    return result.get('url')
                print(f'[ImageHosting] Upload rejected (attempt {attempt}): {result}')
            except requests.Timeout:
                print(
                    f'[ImageHosting] Timeout (attempt {attempt}) for {image_url[:60]}...'
                )
            except Exception as e:
                print(f'[ImageHosting] Error (attempt {attempt}): {e}')

            if attempt < max_retries:
                wait = 2 ** (attempt - 1)
                print(f'[ImageHosting] Retrying in {wait}s...')
                time.sleep(wait)

        return None

    def get_all_images(self) -> dict:
        """游标分页遍历 entries API，返回 {url: {"id": file_id, "created_at": created_at}} 字典"""
        result = {}
        params = {'limit': 100}
        max_retries = 3
        consecutive_errors = 0
        while True:
            try:
                resp = requests.get(
                    'https://www.superbed.cc/api/v1/entries/',
                    headers={'X-API-Key': self.token},
                    params=params,
                    timeout=30)
                data = resp.json()
                for entry in data.get('entries', []):
                    if entry.get('type') != 'file':
                        continue
                    url = entry.get('url', '')
                    if url:
                        result[url] = {
                            'id': entry.get('id', ''),
                            'created_at': entry.get('created_at', ''),
                        }
                consecutive_errors = 0
                if not data.get('has_more'):
                    break
                params['before'] = data.get('next_cursor')
            except Exception as e:
                consecutive_errors += 1
                print(f'[ImageHosting] entries error (attempt {consecutive_errors}/{max_retries}): {e}')
                if consecutive_errors >= max_retries:
                    break
                time.sleep(2 ** (consecutive_errors - 1))
        return result

    def delete_images(self, file_ids: list) -> tuple:
        """批量删除 CDN 图片（通过 file_id），返回 (success: bool, msg: str)"""
        if not file_ids:
            return True, ''
        try:
            resp = requests.post(
                'https://www.superbed.cc/api/v1/files/batch/delete',
                headers={'X-API-Key': self.token},
                json={'file_ids': file_ids},
                timeout=30)
            data = resp.json()
            failed = data.get('failed_count', 0)
            if failed:
                return False, data.get('message', f'{failed} failed')
            return True, data.get('message', '')
        except Exception as e:
            return False, str(e)

    def upload_file(self, file_data: bytes,
                    filename: str = None,
                    max_retries: int = 3) -> Optional[str]:
        for attempt in range(1, max_retries + 1):
            try:
                files = {'file': (filename or 'image.jpg', file_data)}
                resp = requests.post(self.upload_url,
                                     data={'token': self.token},
                                     files=files,
                                     timeout=60)
                result = resp.json()
                if result.get('err') == 0:
                    return result.get('url')
                print(f'[ImageHosting] File upload rejected (attempt {attempt}): {result}')
            except requests.Timeout:
                print(f'[ImageHosting] File upload timeout (attempt {attempt})')
            except Exception as e:
                print(f'[ImageHosting] File upload error (attempt {attempt}): {e}')

            if attempt < max_retries:
                wait = 2 ** (attempt - 1)
                print(f'[ImageHosting] Retrying in {wait}s...')
                time.sleep(wait)

        return None


def get_service() -> ImageHostingService:
    """根据配置返回当前使用的图片托管服务实例"""
    service_name = getattr(settings, 'IMAGE_HOSTING_SERVICE', 'superbed')

    if service_name == 'superbed':
        return SuperBedService(token=settings.SUPERBED_TOKEN)

    raise ValueError(f'Unknown image hosting service: {service_name}')


def upload_image(image_url: str) -> Optional[str]:
    """通过 URL 上传图片到当前托管服务"""
    return get_service().upload_by_url(image_url)


def upload_image_file(file_data: bytes, filename: str = None) -> Optional[str]:
    """通过文件上传图片到当前托管服务"""
    return get_service().upload_file(file_data, filename)


def get_all_cdn_images() -> dict:
    """获取 CDN 上所有图片 {url: {"id": file_id, "created_at": created_at}} 字典"""
    return get_service().get_all_images()


def delete_cdn_images(file_ids: list) -> tuple:
    """批量删除 CDN 图片（通过 file_id），返回 (success: bool, msg: str)"""
    return get_service().delete_images(file_ids)


# ======================
# eBay 图片识别（与服务无关，保留在此）
# ======================
EBAY_IMAGE_DOMAINS = ['ebayimg.com', 'ebay.com']


def is_ebay_image(url: str) -> bool:
    if not url:
        return False
    return any(d in url for d in EBAY_IMAGE_DOMAINS)
