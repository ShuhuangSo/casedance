import os
import requests
import re
import time
import datetime
from django.db import connection, transaction, close_old_connections
from django.db.models import Max, Q
from django.conf import settings
from casedance.celery import app
from productbase.image_hosting import upload_image, is_ebay_image
from productbase.models import log_product_action

# 🔥 换成新模型
from productbase.models import (BaseProductGroup, ProductGroup, ProductCore,
                                ProductShop, ProductImage, ShopConfig)
from django.contrib.auth import get_user_model

User = get_user_model()

# =====================
# 自定义属性保留白名单
# =====================
keep_attributes_list = ['Compatible Model', 'Material', 'Type', 'Style', 'Compatible Brand']

# =====================
# 定价公式 验证 & 求值
# =====================
import ast

_FORMULA_ALLOWED_VARS = {'price', 'cost'}  # 允许的变量名
_FORMULA_ALLOWED_NODES = {
    ast.Expression, ast.Compare, ast.BoolOp, ast.BinOp, ast.UnaryOp,
    ast.IfExp, ast.Num, ast.Name, ast.Load, ast.Constant,
    ast.Eq, ast.NotEq, ast.Lt, ast.Gt, ast.LtE, ast.GtE,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.And, ast.Or,
    ast.NameConstant, ast.In, ast.NotIn,
}

_SAFE_BUILTINS = {
    'True': True, 'False': False, 'None': None,
    'abs': abs, 'min': min, 'max': max, 'round': round,
}


def _prepare_formula(formula):
    """将 {price} 替换为 price，便于 AST 解析"""
    s = formula.strip()
    for var in _FORMULA_ALLOWED_VARS:
        s = s.replace('{%s}' % var, var)
    return s


def validate_formula(formula):
    """
    验证定价公式是否有效。返回 (is_valid, error_msg)。
    安全约束：仅允许算术/比较/条件表达式 + 白名单变量。
    """
    if not formula or not formula.strip():
        return False, "公式不能为空"
    try:
        tree = ast.parse(_prepare_formula(formula), mode='eval')
    except SyntaxError as e:
        return False, f"公式语法错误: {e}"

    # 检查所有节点类型
    for node in ast.walk(tree):
        if type(node) not in _FORMULA_ALLOWED_NODES:
            return False, f"公式包含不允许的操作: {type(node).__name__}"
        if isinstance(node, ast.Name):
            if node.id not in _FORMULA_ALLOWED_VARS and node.id not in _SAFE_BUILTINS:
                return False, f"不允许的变量: {node.id}（仅允许 {', '.join(sorted(_FORMULA_ALLOWED_VARS))}）"

    # 试算验证
    try:
        compiled = compile(tree, '<formula>', 'eval')
        eval(compiled, {'__builtins__': _SAFE_BUILTINS}, {'price': 1.0, 'cost': 1.0})
    except Exception as e:
        return False, f"公式试算失败: {e}"

    return True, ""


def evaluate_formula(formula, **variables):
    """
    求值定价公式。variables 传入 price/cost 等。
    公式已验证过，此处不做安全检查。
    """
    tree = ast.parse(_prepare_formula(formula), mode='eval')
    compiled = compile(tree, '<formula>', 'eval')
    # 为未传入的变量补默认值 0
    env = {v: variables.get(v, 0) for v in _FORMULA_ALLOWED_VARS}
    return float(eval(compiled, {'__builtins__': _SAFE_BUILTINS}, env))


def apply_pricing_rule(original_price, pricing_rule):
    """
    对原价应用定价规则，返回最终价格。
    返回 (final_price, log_detail)。
    """
    if not pricing_rule:
        return original_price, None

    formula = pricing_rule.formula
    target = evaluate_formula(formula, price=float(original_price))

    log_parts = [f'规则:"{pricing_rule.name}"', f'原价:{original_price}']

    # 最低限价
    if pricing_rule.min_price is not None and target < pricing_rule.min_price:
        final = pricing_rule.min_price
        log_parts.append(f'目标:{target}→限价下限:{final}')
        return float(final), ' | '.join(log_parts)

    # 最高限价
    if pricing_rule.max_price is not None and target > pricing_rule.max_price:
        final = pricing_rule.max_price
        log_parts.append(f'目标:{target}→限价上限:{final}')
        return float(final), ' | '.join(log_parts)

    # 无限制且 <= 0 → 保留原价
    if target <= 0:
        log_parts.append(f'目标:{target}≤0→保留原价')
        return float(original_price), ' | '.join(log_parts)

    log_parts.append(f'目标:{target}')
    return float(target), ' | '.join(log_parts)


def format_sku_from_id(pk):
    """根据自增 ID 生成 SKU 编码"""
    if pk < 100000:
        return f"Z{pk:05d}"
    elif pk < 1000000:
        return f"Z{pk:06d}"
    elif pk < 10000000:
        return f"Z{pk:07d}"
    else:
        return f"Z{pk}"


def assign_sku_after_save(core):
    """
    保存 ProductCore 后，基于数据库分配的自增 ID 设置 SKU。
    替代之前 generate_unique_sku() 的 Max('id') 预测方案，避免并发竞态导致的
    Duplicate entry 错误。
    """
    core.sku = format_sku_from_id(core.id)
    core.save(update_fields=['sku'])


def generate_unique_sku():
    """
    生成唯一 SKU（兼容旧接口，内部用 uuid 避免并发冲突）。
    新代码应使用 assign_sku_after_save() 方案。
    """
    import uuid
    return f"TMP{uuid.uuid4().hex[:12]}"


def remove_emoji_special(text):
    if not text:
        return ""
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002500-\U00002BEF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642"
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"
        u"\u3030"
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub("", text)
    text = text.encode("utf-8", "ignore").decode("utf-8")
    return text


def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&[a-zA-Z0-9#]+;', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = remove_emoji_special(text)
    return text


def get_variant_names(parsed_items, varies_by=None):
    """
    获取变体维度名。优先使用 eBay 原生 variesByLocalizedAspects，
    兜底用旧逻辑对比 localizedAspects。
    """
    if varies_by:
        return ",".join(v.strip().lower() for v in varies_by)

    # 兜底：对比相邻 item 的 localizedAspects
    all_aspects = []
    for item in parsed_items:
        asp = {(a["name"].strip().lower(), a["value"])
               for a in item.get("localizedAspects", [])}
        all_aspects.append(asp)

    if len(all_aspects) <= 1:
        return ""

    diff_keys = set()
    for i in range(len(all_aspects) - 1):
        current = all_aspects[i]
        next_one = all_aspects[i + 1]
        diff = current.symmetric_difference(next_one)
        for k, v in diff:
            diff_keys.add(k.strip().lower())

    return ",".join(sorted(list(diff_keys)))


def detect_primary_variant(items, variant_keys):
    """
    推断主属性（控制图片切换的维度）。
    对每个维度，按该维度值分组，检查组内图片是否一致。
    如果某维度所有组的图片都一致 → 该维度是主属性。
    兜底返回第一个维度。
    """
    if len(variant_keys) <= 1:
        return variant_keys[0] if variant_keys else ""

    # 构建索引：{dim_index: {value: set_of_images}}
    for dim_idx, _ in enumerate(variant_keys):
        dim_images = {}  # {value: set of image_urls}
        for item in items:
            aspects = item.get("localizedAspects", [])
            asp_dict = {a["name"].strip().lower(): a["value"].strip()
                        for a in aspects}
            val = asp_dict.get(variant_keys[dim_idx], "")
            img = item.get("image", "")
            if val not in dim_images:
                dim_images[val] = set()
            dim_images[val].add(img)

        # 如果每个值对应唯一图片 → 这是主属性
        if dim_images and all(len(imgs) == 1 for imgs in dim_images.values()):
            return variant_keys[dim_idx]

    # 兜底：第一个维度
    return variant_keys[0]


# ======================
# eBay 配置
# ======================
# eBay 凭证从环境变量读取
EBAY_REDIRECT_URI = "https://localhost:8000/callback"

_ebay_access_token = None
_ebay_token_invalid = True


def get_valid_token():
    global _ebay_access_token, _ebay_token_invalid

    if not _ebay_token_invalid and _ebay_access_token:
        return _ebay_access_token

    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type":
        "application/x-www-form-urlencoded",
        "Authorization":
        requests.auth._basic_auth_str(settings.EBAY_CLIENT_ID,
                                        settings.EBAY_CLIENT_SECRET)
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
        "redirect_uri": EBAY_REDIRECT_URI
    }

    try:
        resp = requests.post(url, headers=headers, data=data, timeout=10)
        resp.raise_for_status()
        token_data = resp.json()
        _ebay_access_token = token_data["access_token"]
        _ebay_token_invalid = False
        return _ebay_access_token
    except Exception as e:
        print(f"❌ Token 获取失败: {str(e)}")
        return None


def parse_single_item(item):
    price = item.get("price", {})
    title = remove_emoji_special(item.get("title", ""))
    return {
        "title":
        title,
        "price_value":
        price.get("value", ""),
        "price_currency":
        price.get("currency", ""),
        "categoryPath":
        item.get("categoryPath", ""),
        "categoryIdPath":
        item.get("categoryIdPath", ""),
        "image":
        item.get("image", {}).get("imageUrl", ""),
        "additionalImages":
        [img.get("imageUrl", "") for img in item.get("additionalImages", [])],
        "localizedAspects":
        item.get("localizedAspects", [])
    }


def generate_p_name(supplier, series, variant_keys, var_values, var_mappings):
    """
    根据供应商、系列、变体值和翻译映射生成中文名称。
    格式：供应商-系列-变体1-变体2-...
    var_mappings: {"colour": {"Black": "黑色"}, "model": {"iPhone 14": "iPhone 14"}}
    """
    parts = []
    if supplier:
        parts.append(supplier.strip())
    if series:
        parts.append(series.strip())

    for i, vname in enumerate(variant_keys):
        if i >= len(var_values):
            break
        original = var_values[i]
        if not original:
            continue
        mapping = var_mappings.get(vname, {})
        translated = mapping.get(original, original)
        parts.append(translated)

    return "-".join(parts) if parts else "默认中文名称"


def regenerate_p_names(base):
    """
    当 supplier/series/var_mappings 更新后，重新生成该 BaseProductGroup 下
    所有 ProductCore 的 p_name。
    """
    base.refresh_from_db()
    supplier = base.supplier
    series = base.series
    var_mappings = base.var_mappings or {}

    # 获取主店铺的 variant_keys
    main_group = base.product_groups.filter(is_main=True).first()
    if not main_group:
        main_group = base.product_groups.first()
    if not main_group:
        return 0

    variant_keys = main_group.get_variant_names()

    updated = 0
    for core in base.core_skus.all():
        # 找到该 core_sku 对应的 shop_sku（在主店铺下）
        shop_sku = core.shop_records.filter(group=main_group).first()
        if not shop_sku:
            continue
        var_values = [shop_sku.var1, shop_sku.var2, shop_sku.var3, shop_sku.var4]
        new_p_name = generate_p_name(supplier, series, variant_keys,
                                     var_values, var_mappings)
        if core.p_name != new_p_name:
            core.p_name = new_p_name
            core.save(update_fields=['p_name'])
            updated += 1

    return updated


def apply_variant_mapping(variant_keys, var_values):
    """
    将变体映射规则应用到原始变体值上。
    每个变体维度独立匹配：只要 variant_key 匹配某个 VariantMappingAttribute.attribute_name，
    就应用其 values 替换规则。未设置映射的维度保持原值。

    Args:
        variant_keys: 已小写的变体维度名列表，如 ['color', 'model']
        var_values: 原始变体值列表，如 ['Red', 'For Samsung A16']

    Returns:
        映射后的 var_values 列表（长度与输入相同）
    """
    from productbase.models import VariantMappingAttribute

    mapped = list(var_values)
    if not variant_keys or not var_values:
        return mapped

    # 加载所有映射属性及其值，支持逗号分隔多个名称
    attrs = VariantMappingAttribute.objects.prefetch_related('values').all()
    name_to_attr = {}
    for a in attrs:
        names = [n.strip().lower() for n in a.attribute_name.split(",") if n.strip()]
        for n in names:
            name_to_attr[n] = a

    for i, vk in enumerate(variant_keys):
        attr_entry = name_to_attr.get(vk)
        if attr_entry is None:
            continue

        raw_val = var_values[i]
        if not raw_val:
            continue

        for val_rule in attr_entry.values.all():
            pattern = val_rule.match_pattern
            if raw_val.lower().startswith(pattern.lower()):
                suffix = raw_val[len(pattern):]
                mapped[i] = val_rule.replace_value + suffix
                break  # 第一个匹配的值规则胜出

    return mapped


def match_warehouse(category_id, category_name):
    """
    根据类目匹配仓库及 MB 产品状态。

    返回 (warehouse, mb_product_status) 元组。

    匹配优先级：
    1) category_id 精确匹配
    2) category_name 子串匹配（大小写不敏感）
    3) 兜底：category_id 和 category_name 均为空的规则
    4) 硬编码兜底：'F仓', ''
    """
    from productbase.models import WarehouseConfig

    configs = WarehouseConfig.objects.all().order_by('-priority')

    # 1) 前缀匹配 category_id（如设置 "15032" 可匹配 "15032|9394|20349"）
    for cfg in configs:
        if cfg.category_id and (category_id or '').strip().startswith(cfg.category_id.strip()):
            return cfg.warehouse, cfg.mb_product_status or ''

    # 2) 子串匹配 category_name
    for cfg in configs:
        if cfg.category_name and cfg.category_name.strip().lower() in (category_name or '').lower():
            return cfg.warehouse, cfg.mb_product_status or ''

    # 3) 兜底规则（category_id 和 category_name 均为空）
    fallback = configs.filter(category_id='', category_name='').first()
    if fallback:
        return fallback.warehouse, fallback.mb_product_status or ''

    # 4) 硬编码兜底
    return 'F仓', ''


def build_var_mappings_from_config(dim_values):
    """
    根据变体映射配置，为每个维度下的原始值生成中文映射。

    Args:
        dim_values: {'colour': {'Black','Blue'}, 'model': {'For Samsung Galaxy Z Fold 7'}}

    Returns:
        dict like {'colour': {'Black': '黑色', 'Blue': '蓝色'},
                   'model': {'For Samsung Galaxy Z Fold 7': '三星 Galaxy Z Fold 7'}}

    匹配规则：attribute_name 支持逗号分隔多个名称（如 "color,colour"），
    任一名称匹配到维度名即触发。
    """
    from productbase.models import VariantMappingAttribute

    var_mappings = {}
    attrs = VariantMappingAttribute.objects.prefetch_related('values').all()

    # 构建索引：每个独立名称 → 对应的 attribute 条目
    name_to_attr = {}
    for a in attrs:
        names = [n.strip().lower() for n in a.attribute_name.split(",") if n.strip()]
        for n in names:
            name_to_attr[n] = a

    for dim_name, values in dim_values.items():
        attr_entry = name_to_attr.get(dim_name.lower())
        if attr_entry is None:
            continue

        dim_mapping = {}
        for raw_val in values:
            if not raw_val:
                continue
            for val_rule in attr_entry.values.all():
                pattern = val_rule.match_pattern
                if raw_val.lower().startswith(pattern.lower()):
                    suffix = raw_val[len(pattern):]
                    mapped = val_rule.replace_value + suffix
                    if mapped != raw_val:
                        dim_mapping[raw_val] = mapped
                    break  # 第一个匹配的值规则胜出

        if dim_mapping:
            var_mappings[dim_name] = dim_mapping

    return var_mappings


# ======================
# 🔥 核心保存逻辑（已改新结构）
# ======================
@transaction.atomic
def save_product_to_db(data,
                       item_id,
                       marketplace_id,
                       platform="EBAY",
                       supplier=None,
                       series=None,
                       cost=0,
                       creator="system",
                       keep_attributes=None,
                       fixed_attributes=None,
                       fetch_config_name=None):

    if not data or not data["items"]:
        return None

    # 0. 变体检测（需在创建 BaseProductGroup 之前完成）
    first_item = data["items"][0]
    varies_by = data.get("variesBy")
    variant_name = get_variant_names(data["items"], varies_by)
    primary_variant = detect_primary_variant(data["items"],
                                             variant_name.split(',')
                                             if variant_name else [])

    # 1. BaseProductGroup
    base = BaseProductGroup.objects.create(
        p_status="INIT",
        category=first_item["categoryPath"],
        category_id=first_item["categoryIdPath"],
        supplier=supplier or "",
        series=series or "",
        creator=creator,
        from_item_id=item_id,
        from_site_id=marketplace_id,
        from_platform=platform,
        primary_variant=primary_variant)

    desc = (data.get("group_description") or data.get("single_description") or "")

    # 处理自定义属性
    variant_attr_names = [n.strip().lower() for n in variant_name.split(',')]
    custom_attrs = {}
    all_aspects = first_item.get("localizedAspects", [])
    is_single = len(data["items"]) == 1
    attr_list = keep_attributes if keep_attributes is not None else keep_attributes_list
    keep_lower = [k.lower() for k in attr_list]

    for asp in all_aspects:
        name = asp.get("name", "")
        value = asp.get("value", "")
        nl = name.strip().lower()
        if nl not in keep_lower:
            continue
        if not is_single and nl in variant_attr_names:
            continue
        custom_attrs[name] = value

    # 叠加固定附加属性：不在 keep_attributes 中则追加，在则覆盖
    fixed = fixed_attributes or {}
    for attr_name, attr_value in fixed.items():
        custom_attrs[attr_name] = attr_value

    # 2. 查用户的 ShopConfig，确定主店铺和子店铺参数
    user = User.objects.filter(username=creator).first()
    main_config = None
    auto_configs = []
    if user:
        configs = ShopConfig.objects.filter(user=user)
        main_config = configs.filter(is_main=True).first()
        auto_configs = list(
            configs.filter(auto_create_shop=True).exclude(
                pk=main_config.pk if main_config else None))

    # 主店铺参数
    main_shop_account = main_config.shop_account if main_config else "ABY360"
    main_platform = main_config.platform if main_config else "EBAY"
    main_site = main_config.site if main_config else marketplace_id
    main_listing_config = main_config.listing_config if main_config else None
    main_pricing_rule = main_config.pricing_rule if main_config else None

    group_title = data["itemGroupTitle"] or data["items"][0]["title"]

    # 3. 创建主 ProductGroup
    main_pg = ProductGroup.objects.create(
        base=base,
        shop_account=main_shop_account,
        platform=main_platform,
        title=group_title,
        site=main_site,
        variant_name=variant_name,
        is_main=True,
        p_status="INIT",
        desc=desc,
        custom_attributes=custom_attrs,
        listing_config=main_listing_config)

    # 4. 组图片（主店铺）
    if data.get("itemGroupImage"):
        ProductImage.objects.create(base_group=base,
                                    group=main_pg,
                                    image_url=data["itemGroupImage"],
                                    is_cover=True,
                                    sort=0)

    additional_images = data.get("itemGroupAdditionalImages") or []
    for i, url in enumerate(additional_images):
        ProductImage.objects.create(group=main_pg, image_url=url, sort=i + 1)

    variant_keys = main_pg.get_variant_names()
    original_prices = {}  # core_sku → 原价，供子店铺独立定价

    pricing_logs = set()  # 收集哪些店铺应用了定价规则

    # 5. 遍历变体 → 创建 ProductCore + ProductShop（主店铺）
    for item in data["items"]:
        asp_dict = {
            a["name"].strip().lower(): a["value"]
            for a in item.get("localizedAspects", [])
        }

        var1 = asp_dict.get(variant_keys[0] if len(variant_keys) > 0 else "",
                            "")
        var2 = asp_dict.get(variant_keys[1] if len(variant_keys) > 1 else "",
                            "")
        var3 = asp_dict.get(variant_keys[2] if len(variant_keys) > 2 else "",
                            "")
        var4 = asp_dict.get(variant_keys[3] if len(variant_keys) > 3 else "",
                            "")

        try:
            original_price = float(
                item["price_value"]) if item["price_value"] else 0
        except:
            original_price = 0

        # 应用定价规则
        final_price, log_detail = apply_pricing_rule(
            original_price, main_pricing_rule)

        p_name = generate_p_name(supplier, series,
                                 variant_keys,
                                 [var1, var2, var3, var4],
                                 base.var_mappings)
        warehouse, mb_status = match_warehouse(
            base.category_id, base.category)
        core_sku = ProductCore.objects.create(base=base,
                                              sku=generate_unique_sku(),
                                              p_name=p_name,
                                              UPC="",
                                              cost=cost if cost > 0 else 0,
                                              purchase_url="",
                                              warehouse=warehouse,
                                              mb_product_status=mb_status)
        assign_sku_after_save(core_sku)
        original_prices[core_sku.id] = original_price

        ProductShop.objects.create(group=main_pg,
                                   core_sku=core_sku,
                                   title=item["title"],
                                   desc=desc,
                                   price=final_price,
                                   currency=item["price_currency"] or "USD",
                                   var1=var1,
                                   var2=var2,
                                   var3=var3,
                                   var4=var4,
                                   custom_attributes=None)

        if log_detail:
            pricing_logs.add(
                f'{main_pg.shop_account}: "{main_pricing_rule.name}"')

        # 图片（绑定 core_sku）
        is_single_variant = not data.get("itemGroupImage")
        if is_single_variant:
            if item.get("image"):
                ProductImage.objects.create(base_group=base,
                                            group=main_pg,
                                            product_core=core_sku,
                                            image_url=item["image"],
                                            is_cover=True,
                                            sort=0)
            for j, url in enumerate(item.get("additionalImages", [])):
                ProductImage.objects.create(group=main_pg,
                                            product_core=core_sku,
                                            image_url=url,
                                            sort=j + 1)
        else:
            if item.get("image"):
                ProductImage.objects.create(product_core=core_sku,
                                            image_url=item["image"],
                                            is_cover=True,
                                            sort=0)
            for j, url in enumerate(item.get("additionalImages", [])):
                ProductImage.objects.create(product_core=core_sku,
                                            image_url=url,
                                            sort=j + 1)

    # 5b. 根据变体映射配置填充 base.var_mappings，再重新生成 p_name
    if variant_keys:
        # 收集每个维度下的所有变体值
        dim_values = {vk: set() for vk in variant_keys}
        var_field_map = {0: 'var1', 1: 'var2', 2: 'var3', 3: 'var4'}
        for shop_sku in main_pg.shop_skus.all():
            for i, vk in enumerate(variant_keys):
                val = getattr(shop_sku, var_field_map[i], '')
                if val:
                    dim_values[vk].add(val)

        var_mappings = build_var_mappings_from_config(dim_values)
        if var_mappings:
            # 合并到已有的 var_mappings（保留手动编辑的部分）
            existing = base.var_mappings or {}
            for dim, mapping in var_mappings.items():
                if dim in existing:
                    existing[dim].update(mapping)
                else:
                    existing[dim] = mapping
            base.var_mappings = existing
            base.save(update_fields=['var_mappings'])
            # 重新生成所有 SKU 的中文名称
            regenerate_p_names(base)
            # 记录操作日志
            parts = []
            for dim, mapping in var_mappings.items():
                parts.append(f'{dim} {len(mapping)}个')
            log_product_action(base, 'VARIANT',
                               f'变体映射: {", ".join(parts)}',
                               operator=creator)

    # 6. 为 auto_create_shop 配置创建子店铺（复制主店铺内容）
    for config in auto_configs:
        child_pg = ProductGroup.objects.create(
            base=base,
            shop_account=config.shop_account,
            platform=config.platform,
            title=group_title,
            site=config.site,
            variant_name=variant_name,
            is_main=False,
            p_status="INIT",
            desc=desc,
            custom_attributes=custom_attrs,
            listing_config=config.listing_config)

        # 拷贝组图片
        for img in main_pg.images.all():
            ProductImage.objects.create(base_group=base,
                                        group=child_pg,
                                        image_url=img.image_url,
                                        is_cover=img.is_cover,
                                        sort=img.sort)

        child_pricing_rule = config.pricing_rule

        # 拷贝 ProductShop（每个 ProductCore 一条）
        for main_shop in main_pg.shop_skus.all():
            # 子店铺独立计算定价（使用原价 + 自己的定价规则）
            orig_price = original_prices.get(main_shop.core_sku_id,
                                             float(main_shop.price))
            child_price, child_log = apply_pricing_rule(
                orig_price, child_pricing_rule)

            ProductShop.objects.create(
                group=child_pg,
                core_sku=main_shop.core_sku,
                title=main_shop.title,
                desc=main_shop.desc,
                price=child_price,
                currency=main_shop.currency,
                var1=main_shop.var1,
                var2=main_shop.var2,
                var3=main_shop.var3,
                var4=main_shop.var4,
                custom_attributes=main_shop.custom_attributes)

            if child_log:
                pricing_logs.add(
                    f'{child_pg.shop_account}: "{child_pricing_rule.name}"')

    # 记录创建日志（含所有店铺账号 + 抓取配置）
    shop_accounts = [pg.shop_account for pg in base.product_groups.all()]
    create_detail = f'从 {platform} 抓取商品 {item_id}，创建店铺: {", ".join(shop_accounts)}'
    if fetch_config_name:
        create_detail += f'，抓取配置: {fetch_config_name}'
    log_product_action(base, 'CREATE', create_detail, operator=creator)

    # 记录仓库匹配
    if variant_keys:
        first_core = base.core_skus.first()
        if first_core and first_core.warehouse:
            log_product_action(base, 'WAREHOUSE',
                               f'仓库匹配: {first_core.warehouse}',
                               operator=creator)

    # 记录定价日志
    if pricing_logs:
        log_product_action(base, 'PRICE_RULE',
                           '、'.join(sorted(pricing_logs)), operator=creator)

    return base, main_pg


def get_ebay_product(item_id: str, marketplace_id: str):
    token = get_valid_token()
    if not token:
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": marketplace_id,
        "Accept": "application/json"
    }

    group_url = f"https://api.ebay.com/buy/browse/v1/item/get_items_by_item_group?item_group_id={item_id}"
    resp = requests.get(group_url, headers=headers, timeout=15)

    if resp.status_code == 401:
        global _ebay_token_invalid
        _ebay_token_invalid = True
        return get_ebay_product(item_id, marketplace_id)

    result = {
        "items": [],
        "itemGroupTitle": None,
        "itemGroupImage": None,
        "itemGroupAdditionalImages": None,
        "group_description": None,
        "single_description": None,
        "variesBy": [],
    }

    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", [])
        for item in items:
            result["items"].append(parse_single_item(item))
        if items:
            first = items[0]
            pig = first.get("primaryItemGroup", {})
            result["itemGroupTitle"] = pig.get("itemGroupTitle", "")
            result["itemGroupImage"] = pig.get("itemGroupImage",
                                               {}).get("imageUrl", "")
            result["variesBy"] = [
                a.get("localizedAspectName", "")
                for a in pig.get("variesByLocalizedAspects", [])
            ]
            result["itemGroupAdditionalImages"] = [
                img.get("imageUrl", "")
                for img in pig.get("itemGroupAdditionalImages", [])
            ]
            common = data.get("commonDescriptions", [])
            if common:
                result["group_description"] = clean_html(common[0].get(
                    "description", ""))
    else:
        single_url = f"https://api.ebay.com/buy/browse/v1/item/v1|{item_id}|0"
        s_resp = requests.get(single_url, headers=headers, timeout=15)
        if s_resp.status_code != 200:
            return None
        item_data = s_resp.json()
        result["items"].append(parse_single_item(item_data))
        result["single_description"] = clean_html(
            item_data.get("description", ""))

    return result


def print_final_data(data):
    if not data:
        return
    print("\n" + "=" * 90)
    print("📋 最终提取商品字段")
    print("=" * 90)
    if data["itemGroupTitle"]:
        print(f"\n【组标题】{data['itemGroupTitle']}")
    for idx, item in enumerate(data["items"]):
        print(
            f"\n{item['title']} | {item['price_value']}{item['price_currency']}"
        )


# ======================
# 异步抓取任务（Celery）
# ======================
@app.task(bind=True, max_retries=2)
def fetch_ebay_product_async(self,
                              task_id,
                              supplier=None,
                              series=None,
                              cost=0,
                              creator="system",
                              keep_attributes=None,
                              fixed_attributes=None,
                              fetch_config_name=None):
    """
    Celery 异步抓取 eBay 商品。前端创建 FetchTask(PENDING) 后立即返回，
    后台异步完成抓取并更新 FetchTask 状态。
    """
    from productbase.models import FetchTask
    from django.utils import timezone as dj_timezone

    # 恢复卡住的 PROCESSING 任务：超过 30 分钟仍在处理中的重置为 PENDING
    stuck_deadline = dj_timezone.now() - datetime.timedelta(minutes=30)
    recovered = FetchTask.objects.filter(
        status='PROCESSING', update_time__lt=stuck_deadline
    ).update(status='PENDING', log='任务超时，自动重置为等待抓取')
    if recovered:
        print(f'[FETCH] Recovered {recovered} stuck PROCESSING tasks → PENDING')

    try:
        task = FetchTask.objects.get(id=task_id)
    except FetchTask.DoesNotExist:
        print(f'[FETCH] Task {task_id} not found')
        return {'status': 'FAILED', 'error': 'Task not found'}

    task.status = "PROCESSING"
    task.log = "开始抓取..."
    task.save()

    try:
        base_group = fetch_and_save_ebay_product_with_task(
            task,
            supplier=supplier,
            series=series,
            cost=cost,
            creator=creator,
            keep_attributes=keep_attributes,
            fixed_attributes=fixed_attributes,
            fetch_config_name=fetch_config_name)

        task.status = "SUCCESS"
        task.log = "✅ 抓取成功"
        task.base_group = base_group
        task.save()
        return {
            'status': 'SUCCESS',
            'task_id': task.id,
            'base_group_id': base_group.id
        }

    except Exception as e:
        task.status = "FAILED"
        task.log = f"❌ 异常：{str(e)}"
        task.save()
        return {'status': 'FAILED', 'task_id': task.id, 'error': str(e)}


# ======================
# 任务入口（同步，供异步任务内部调用）
# ======================
def fetch_and_save_ebay_product_with_task(task,
                                          supplier=None,
                                          series=None,
                                          cost=0,
                                          creator="system",
                                          keep_attributes=None,
                                          fixed_attributes=None,
                                          fetch_config_name=None):
    item_id = task.item_id
    marketplace_id = task.marketplace_id
    platform = task.platform

    product_data = get_ebay_product(item_id, marketplace_id)
    print_final_data(product_data)

    if not product_data:
        raise Exception("未获取到商品数据")

    base_group, _ = save_product_to_db(product_data,
                                       item_id,
                                       marketplace_id,
                                       platform=platform,
                                       supplier=supplier,
                                       series=series,
                                       cost=cost,
                                       creator=creator,
                                       keep_attributes=keep_attributes,
                                       fixed_attributes=fixed_attributes,
                                       fetch_config_name=fetch_config_name)

    check_and_update_base_status([base_group.id])
    return base_group


# ======================
# 🔥 状态检查（已改新表）
# 图片上传 → productbase/image_hosting.py（独立模块，可切换服务商）



def _cdn_rate_limit_wait(redis_conn):
    max_per_hour = getattr(settings, 'CDN_RATE_LIMIT_PER_HOUR', 1000)
    """
    滑动窗口速率限制。
    用 Redis Sorted Set 记录过去 1h 内的上传时间戳。
    返回需要等待的秒数（0 表示可立即上传）。
    """
    now = time.time()
    cutoff = now - 3600

    # 清理超过 1 小时的记录
    redis_conn.zremrangebyscore('cdn_upload_ts', 0, cutoff)
    count = redis_conn.zcard('cdn_upload_ts')

    if count < max_per_hour:
        return 0

    # 已达上限，等到最旧的记录过期
    oldest = redis_conn.zrange('cdn_upload_ts', 0, 0, withscores=True)
    if oldest:
        wait = oldest[0][1] + 3600 - now + 0.5
        return max(0, wait)
    return 60


def _cdn_rate_limit_record(redis_conn):
    """记录一次上传的时间戳"""
    redis_conn.zadd('cdn_upload_ts', {str(time.time()): time.time()})
    redis_conn.expire('cdn_upload_ts', 7200)


@app.task(bind=True, max_retries=5, time_limit=7200, soft_time_limit=6900)
def migrate_images_to_cdn(self, base_id):
    """
    Celery 异步任务：将 BaseProductGroup 下所有 eBay 图片迁移到聚合图床。
    - 滑动窗口限速: 1000张/小时（用 Redis Sorted Set），空闲时全速上传
    - 每上传成功一张立即写入 DB，确保重试不丢失进度
    - 异常时自动 retry（countdown=300s=5min）
    """
    from productbase.models import ProductImage, ProductGroup, ProductCore
    from celery.exceptions import SoftTimeLimitExceeded
    import redis as redis_lib

    # Redis 限速连接（用 db=2，不与 Celery broker/result 冲突）
    redis_conn = redis_lib.Redis(
        host=os.environ.get('REDIS_HOST', '127.0.0.1'),
        port=int(os.environ.get('REDIS_PORT', '6379')),
        db=2,
        decode_responses=False)

    close_old_connections()

    # 1. 查所有图片
    group_ids = ProductGroup.objects.filter(base_id=base_id).values_list(
        'id', flat=True)
    core_ids = ProductCore.objects.filter(base_id=base_id).values_list(
        'id', flat=True)

    images = ProductImage.objects.filter(
        Q(base_group_id=base_id)
        | Q(group_id__in=group_ids)
        | Q(product_core_id__in=core_ids))

    ebay_images = [img for img in images if is_ebay_image(img.image_url)]

    if not ebay_images:
        print(f'[CDN] Base {base_id}: no eBay images to migrate')
        update_image_migrated_status(base_id)
        return {'total': 0, 'migrated': 0, 'failed': 0}

    # 2. 按 URL 去重，构建 url → [image_ids] 映射
    url_map = {}
    for img in ebay_images:
        url_map.setdefault(img.image_url, []).append(img.id)

    unique_urls = list(url_map.keys())
    print(f'[CDN] Base {base_id}: {len(ebay_images)} images, '
          f'{len(unique_urls)} unique URLs to migrate')

    # 3. 逐个上传，每张成功后立即写入 DB
    migrated = 0
    failed = 0
    failed_urls = []
    updated_records = 0

    try:
        for i, old_url in enumerate(unique_urls):
            # 速率限制检查
            wait = _cdn_rate_limit_wait(redis_conn)
            if wait > 0:
                print(f'[CDN] Rate limited, waiting {wait:.0f}s...')
                time.sleep(wait)

            print(f'[CDN] [{i+1}/{len(unique_urls)}] Uploading: {old_url[:70]}...')
            new_url = upload_image(old_url)

            if new_url:
                img_ids = url_map[old_url]
                with transaction.atomic():
                    ProductImage.objects.filter(
                        id__in=img_ids).update(image_url=new_url)
                updated_records += len(img_ids)
                migrated += 1
                _cdn_rate_limit_record(redis_conn)
                print(f'[CDN] [{i+1}/{len(unique_urls)}] OK ({len(img_ids)} records)')
            else:
                failed += 1
                failed_urls.append(old_url)
                print(f'[CDN] [{i+1}/{len(unique_urls)}] FAILED')

    except SoftTimeLimitExceeded:
        print(f'[CDN] Base {base_id} soft time limit, retrying...')
        raise self.retry(countdown=300)
    except Exception as e:
        print(f'[CDN] Base {base_id} error: {e}, retrying...')
        raise self.retry(exc=e, countdown=300)

    # 4. 刷新迁移状态 + 记录日志
    result = {
        'total': len(ebay_images),
        'unique_urls': len(unique_urls),
        'migrated': migrated,
        'failed': failed,
        'updated_records': updated_records,
    }
    if failed_urls:
        result['failed_urls'] = failed_urls
    print(f'[CDN] Base {base_id} done: {result}')

    try:
        base = BaseProductGroup.objects.get(id=base_id)
        if migrated > 0 or failed > 0:
            if failed > 0:
                log_product_action(base, 'IMAGE_MIGRATE',
                                   f'图片迁移部分完成：{migrated}/{len(unique_urls)} 成功，{failed} 失败。'
                                   f'失败 URL：{", ".join(failed_urls[:5])}')
            else:
                log_product_action(base, 'IMAGE_MIGRATE',
                                   f'迁移 {migrated} 张图片（{updated_records} 条记录更新）')
        update_image_migrated_status(base_id)
    except BaseProductGroup.DoesNotExist:
        pass
    return result


def check_has_ebay_images(base_id):
    """检查产品下是否还有 eBay 来源的图片"""
    from productbase.models import ProductImage
    from productbase.image_hosting import EBAY_IMAGE_DOMAINS
    group_ids = list(
        ProductGroup.objects.filter(base_id=base_id).values_list('id', flat=True))
    core_ids = list(
        ProductCore.objects.filter(base_id=base_id).values_list('id', flat=True))
    base_qs = ProductImage.objects.filter(
        Q(base_group_id=base_id) | Q(group_id__in=group_ids)
        | Q(product_core_id__in=core_ids))
    q = Q()
    for domain in EBAY_IMAGE_DOMAINS:
        q |= Q(image_url__contains=domain)
    return base_qs.filter(q).exists()


def update_image_migrated_status(base_id):
    """检查并更新产品的图片迁移状态"""
    has_ebay = check_has_ebay_images(base_id)
    BaseProductGroup.objects.filter(id=base_id).update(
        image_migrated=not has_ebay)


def check_variant_mapped(base):
    """
    检查产品的变体映射是否全部完成。
    无变体时直接返回 True；有变体时要求 var_mappings 中每个值都有非空翻译。
    """
    main_group = base.product_groups.filter(is_main=True).first()
    if not main_group:
        main_group = base.product_groups.first()
    if not main_group or not main_group.variant_name:
        return True  # 无变体，无需映射

    variant_names = main_group.get_variant_names()
    if not variant_names:
        return True

    var_map = {0: 'var1', 1: 'var2', 2: 'var3', 3: 'var4'}
    for i, vname in enumerate(variant_names):
        if i > 3:
            break
        dim_mapping = base.var_mappings.get(vname, {})
        attr = var_map[i]
        for shop_sku in main_group.shop_skus.all():
            val = getattr(shop_sku, attr, None)
            if val and not dim_mapping.get(val):
                return False

    return True


def update_variant_mapped_status(base_id):
    """检查并更新产品的变体映射状态"""
    base = BaseProductGroup.objects.get(id=base_id)
    mapped = check_variant_mapped(base)
    BaseProductGroup.objects.filter(id=base_id).update(
        variant_mapped=mapped)


# ======================
def check_and_update_base_status(base_ids):
    if not base_ids:
        return

    for base_id in base_ids:
        try:
            base = BaseProductGroup.objects.get(id=base_id)
            if not base.supplier or not base.series:
                continue

            sku_count = ProductCore.objects.filter(base=base).count()
            if sku_count == 0:
                continue

            invalid_cost = ProductCore.objects.filter(base=base,
                                                      cost__lte=0).exists()
            if not invalid_cost:
                was_init = base.p_status == 'INIT'
                old_status = base.p_status
                base.p_status = "PREPARING"
                base.save(update_fields=['p_status'])

                log_product_action(base, 'STATUS_CHANGE',
                                   f'{old_status} → PREPARING')

                # 检查当前图片迁移状态 & 变体映射状态
                update_image_migrated_status(base_id)
                update_variant_mapped_status(base_id)

                # INIT→PREPARING 时异步触发图片迁移 & AI 自动优化
                if was_init:
                    print(f'[CDN] Dispatching migration for base {base_id}')
                    migrate_images_to_cdn.delay(base_id)
                    auto_optimize_product.delay(base_id)

        except Exception:
            continue


# ======================
# 定时任务：恢复丢失的 PENDING / PROCESSING 抓取任务
# ======================
@app.task
def recover_stuck_fetch_tasks():
    """
    每分钟执行一次，恢复卡住的任务：
    - PROCESSING 超过 30 分钟 → 重置为 PENDING
    （注意：不重复投递 PENDING 任务。Redis 持久化队列，worker 重启不会丢失任务，
     重复投递反而会导致队列中多个相同任务副本，产生重复产品）
    """
    from productbase.models import FetchTask
    from django.utils import timezone as dj_timezone

    now = dj_timezone.now()
    stuck_cutoff = now - datetime.timedelta(minutes=30)
    stuck = FetchTask.objects.filter(
        status='PROCESSING', update_time__lt=stuck_cutoff)
    recovered = 0
    for t in stuck:
        t.status = 'PENDING'
        t.log = '任务超时，自动重置为等待抓取'
        t.save()
        recovered += 1

    if recovered:
        print(f'[RECOVER] Reset {recovered} PROCESSING → PENDING')
    return {'recovered': recovered}


# ======================
# 图片统计 & 清理（异步）
# ======================
@app.task(bind=True, time_limit=600, soft_time_limit=540)
def compute_image_stats(self):
    """异步计算 CDN/DB 图片统计，结果写入 ImageStatsCache"""
    from productbase.models import ImageStatsCache, ProductImage
    from productbase.image_hosting import get_all_cdn_images, is_ebay_image

    cache, _ = ImageStatsCache.objects.get_or_create(id=1)
    cache.computing = True
    cache.save(update_fields=['computing'])

    try:
        # CDN API 可能耗时较长，先关闭 DB 连接避免超时断连
        from django.db import connection
        connection.close()
        cdn_map = get_all_cdn_images()
        cdn_total = len(cdn_map)

        db_urls = set(ProductImage.objects.values_list('image_url', flat=True))
        db_total = len(db_urls)
        unmigrated = sum(1 for u in db_urls if is_ebay_image(u))
        migrated = db_total - unmigrated

        # CDN API 返回的 URL 格式与 DB 中存储的格式不同（/i/ vs /item/），
        # 无法直接 URL 匹配，改用公式估算: orphan = cdn_total - migrated
        orphan = max(0, cdn_total - migrated)

        cache.cdn_total = cdn_total
        cache.db_total = db_total
        cache.migrated = migrated
        cache.unmigrated = unmigrated
        cache.orphan = orphan
        cache.computing = False
        cache.save()
    except Exception as e:
        cache.computing = False
        cache.save(update_fields=['computing'])
        raise e

    return {
        'cdn_total': cache.cdn_total,
        'db_total': cache.db_total,
        'orphan': cache.orphan,
    }


@app.task(bind=True, time_limit=1200, soft_time_limit=1080)
def cleanup_orphan_images(self):
    """异步清理 CDN 孤儿图片。
    注意：CDN API 返回的 URL 格式（/i/xxx）与 DB 存储的旧格式（/item/xxx）不一致，
    无法通过 URL 精确匹配孤儿图片，仅作估算统计，不执行实际删除。
    后续统一 URL 格式后可恢复删除功能。
    """
    from productbase.models import ProductImage, ImageStatsCache
    from productbase.image_hosting import get_all_cdn_images, is_ebay_image
    from django.db import connection

    # CDN API 可能耗时较长，先关闭 DB 连接避免超时断连
    connection.close()
    cdn_map = get_all_cdn_images()
    cdn_total = len(cdn_map)

    db_urls = set(ProductImage.objects.values_list('image_url', flat=True))
    db_total = len(db_urls)
    unmigrated = sum(1 for u in db_urls if is_ebay_image(u))
    migrated = db_total - unmigrated
    orphan = max(0, cdn_total - migrated)

    # 更新统计缓存
    cache, _ = ImageStatsCache.objects.get_or_create(id=1)
    cache.cdn_total = cdn_total
    cache.db_total = db_total
    cache.migrated = migrated
    cache.unmigrated = unmigrated
    cache.orphan = orphan
    cache.computing = False
    cache.save()

    return {
        'orphan': orphan,
        'deleted': 0,
        'note': 'URL 格式不一致（/i/ vs /item/），无法精确删除孤儿图片，仅更新统计',
    }


# ======================
# 自动 AI 优化（主店铺）
# ======================
@app.task(bind=True, max_retries=2)
def auto_optimize_product(self, base_id):
    """
    INIT→PREPARING 时自动触发主店铺标题/描述 AI 优化。
    仅优化主店铺，子店铺直接复制结果。
    """
    from productbase.dify import optimize_product_text, record_dify_usage
    from productbase.models import BaseProductGroup, ShopConfig
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        base = BaseProductGroup.objects.get(id=base_id)
    except BaseProductGroup.DoesNotExist:
        return {'status': 'error', 'msg': '产品不存在'}

    # 仅 PREPARING 状态
    if base.p_status != 'PREPARING':
        return {'status': 'skip', 'msg': '非 PREPARING 状态'}

    # 找用户
    user = User.objects.filter(username=base.creator).first()
    if not user:
        return {'status': 'skip', 'msg': '创建人不存在'}

    # 查主店铺配置
    main_config = ShopConfig.objects.filter(user=user, is_main=True).first()
    if not main_config:
        return {'status': 'skip', 'msg': '无主店铺配置'}

    if not main_config.auto_optimize_title and not main_config.auto_optimize_desc:
        return {'status': 'skip', 'msg': '未开启自动优化'}

    # 找主 ProductGroup
    main_pg = base.product_groups.filter(is_main=True).first()
    if not main_pg:
        main_pg = base.product_groups.first()
    if not main_pg:
        return {'status': 'skip', 'msg': '无店铺'}

    # title_optimized: None=从未优化, False=执行中, True=已完成
    # 只要不等于 None 就说明已处理过，跳过
    if main_config.auto_optimize_title and main_pg.title_optimized is not None:
        main_config.auto_optimize_title = False
    if main_config.auto_optimize_desc and main_pg.desc_optimized is not None:
        main_config.auto_optimize_desc = False

    if not main_config.auto_optimize_title and not main_config.auto_optimize_desc:
        return {'status': 'skip', 'msg': '已优化过'}

    optimized = []

    # 优化标题
    if main_config.auto_optimize_title:
        # 先标记为执行中
        main_pg.title_optimized = False
        main_pg.save(update_fields=['title_optimized'])
        try:
            result, usage, error = optimize_product_text(
                main_pg.id, 'EBAY_TITLE', user=user)
            if not error and result.get('title'):
                new_title = result['title']
                main_pg.title = new_title
                main_pg.title_optimized = True
                main_pg.save(update_fields=['title', 'title_optimized'])
                base.product_groups.filter(is_main=False).update(title=new_title)
                record_dify_usage(user, main_pg, 'EBAY_TITLE', usage)
                tokens = usage.get('total_tokens', 0)
                cost = usage.get('total_price', '0')
                log_product_action(base, 'OPTIMIZE_TITLE',
                                   f'自动优化标题: {tokens} tokens, ¥{cost}')
                optimized.append('标题')
        except Exception as e:
            print(f'[AutoOptimize] title error: {e}')
            raise self.retry(exc=e, countdown=120)

    # 优化描述
    if main_config.auto_optimize_desc:
        main_pg.desc_optimized = False
        main_pg.save(update_fields=['desc_optimized'])
        try:
            result, usage, error = optimize_product_text(
                main_pg.id, 'EBAY_DESC', user=user)
            if not error and result.get('desc'):
                new_desc = result['desc']
                main_pg.desc = new_desc
                main_pg.desc_optimized = True
                main_pg.save(update_fields=['desc', 'desc_optimized'])
                base.product_groups.filter(is_main=False).update(desc=new_desc)
                record_dify_usage(user, main_pg, 'EBAY_DESC', usage)
                tokens = usage.get('total_tokens', 0)
                cost = usage.get('total_price', '0')
                log_product_action(base, 'OPTIMIZE_DESC',
                                   f'自动优化描述: {tokens} tokens, ¥{cost}')
                optimized.append('描述')
        except Exception as e:
            print(f'[AutoOptimize] desc error: {e}')
            raise self.retry(exc=e, countdown=120)

    if optimized:
        print(f'[AutoOptimize] base {base_id}: {"、".join(optimized)} 优化完成')
    return {'status': 'success', 'optimized': optimized}
