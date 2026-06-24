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
        """分页遍历 timeline API，返回 {url: created_at} 字典"""
        result = {}
        page = 1
        page_size = 100
        while True:
            try:
                resp = requests.get(
                    'https://www.superbed.cc/timeline',
                    params={
                        'token': self.token,
                        'f': 'json',
                        'page': page,
                        'size': page_size
                    },
                    timeout=30)
                data = resp.json()
                docs = data.get('docs', [])
                if not docs:
                    break
                for doc in docs:
                    url = doc.get('url', '')
                    if url:
                        result[url] = doc.get('created_at', '')
                total_pages = data.get('pages', 0)
                if page >= total_pages:
                    break
                page += 1
            except Exception as e:
                print(f'[ImageHosting] timeline page {page} error: {e}')
                break
        return result

    def delete_images(self, urls: list) -> tuple:
        """批量删除 CDN 图片，返回 (success: bool, msg: str)"""
        try:
            resp = requests.post(
                'https://www.superbed.cc/delete',
                json={'token': self.token, 'urls': urls},
                timeout=30)
            data = resp.json()
            return data.get('err') == 0, data.get('msg', '')
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
    """获取 CDN 上所有图片 {url: created_at} 字典"""
    return get_service().get_all_images()


def delete_cdn_images(urls: list) -> tuple:
    """批量删除 CDN 图片，返回 (success: bool, msg: str)"""
    return get_service().delete_images(urls)


# ======================
# eBay 图片识别（与服务无关，保留在此）
# ======================
EBAY_IMAGE_DOMAINS = ['ebayimg.com', 'ebay.com']


def is_ebay_image(url: str) -> bool:
    if not url:
        return False
    return any(d in url for d in EBAY_IMAGE_DOMAINS)
