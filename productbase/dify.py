"""
Dify AI 接口封装 — eBay 标题/描述优化
"""
import json
import requests
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

DIFY_HOST = settings.DIFY_HOST
DIFY_API_KEY = settings.DIFY_EBAY_APIKEY
RUN_URL = f"{DIFY_HOST}/v1/workflows/run" if DIFY_HOST else ""


def build_dify_payload(pg, optimize_type):
    """
    构建 Dify workflow 请求 payload。
    pg: ProductGroup 实例
    optimize_type: 'EBAY_TITLE' 或 'EBAY_DESC'
    """
    category = pg.base.category if pg.base else ""
    title = pg.title or ""

    # 构建 variant_list
    variant_list = {}
    if pg.variant_name:
        dims = pg.get_variant_names()
        for i, dim in enumerate(dims):
            if i > 3:
                break
            field = f'var{i+1}'
            vals = pg.shop_skus.values_list(field, flat=True).distinct()
            vals = [v for v in vals if v]
            if vals:
                variant_list[dim] = ", ".join(vals)

    user_value = {
        "id": pg.id,
        "category": category,
    }

    if optimize_type == 'EBAY_TITLE':
        user_value["title"] = title
    elif optimize_type == 'EBAY_DESC':
        user_value["title"] = title
        user_value["variant_list"] = variant_list
        desc = pg.desc or ""
        user_value["desc"] = desc

    return {
        "inputs": {
            "type": optimize_type,
            "user_value": user_value,
        },
        "response_mode": "blocking",
        "user": "管理员",
    }


def optimize_product_text(pg_id, optimize_type, user=None):
    """
    调用 Dify 优化单个店铺的标题或描述。
    返回 (result: dict | None, usage: dict | None, error: str | None)
    """
    if not DIFY_API_KEY or not RUN_URL:
        return None, None, "Dify 配置未设置"

    from productbase.models import ProductGroup
    try:
        pg = ProductGroup.objects.select_related('base').get(id=pg_id)
    except ProductGroup.DoesNotExist:
        return None, None, f"店铺不存在: id={pg_id}"

    payload = build_dify_payload(pg, optimize_type)
    # 将 user 替换为调用人姓名
    if user:
        payload["user"] = user.first_name or user.username

    try:
        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json",
        }
        resp = requests.post(RUN_URL,
                             json=payload,
                             headers=headers,
                             timeout=60)
        data = resp.json()
    except requests.RequestException as e:
        return None, None, f"Dify 请求失败: {str(e)}"
    except json.JSONDecodeError:
        return None, None, f"Dify 返回非 JSON: {resp.text[:200]}"

    if resp.status_code != 200:
        return None, None, f"Dify 返回错误 {resp.status_code}: {data}"

    outputs = data.get("data", {}).get("outputs", {})
    if not outputs:
        return None, None, f"Dify 返回空结果"

    usage = outputs.pop("usage", {})
    result = {
        "id": outputs.get("id", pg_id),
    }
    if optimize_type == 'EBAY_TITLE':
        result["title"] = outputs.get("title", "")
    elif optimize_type == 'EBAY_DESC':
        result["desc"] = outputs.get("desc", "")

    return result, usage, None


def record_dify_usage(user, pg, optimize_type, usage_data):
    """记录 Dify 调用消耗到数据库"""
    from productbase.models import DifyUsageLog
    return DifyUsageLog.objects.create(
        user=user,
        product_group=pg,
        optimize_type=optimize_type,
        prompt_tokens=usage_data.get("prompt_tokens", 0),
        completion_tokens=usage_data.get("completion_tokens", 0),
        total_tokens=usage_data.get("total_tokens", 0),
        total_price=usage_data.get("total_price", "0"),
        currency=usage_data.get("currency", "RMB"),
        latency=usage_data.get("latency", 0),
    )
