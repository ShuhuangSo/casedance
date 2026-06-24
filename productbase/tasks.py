import requests
import re
import time
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
                       fixed_attributes=None):

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

    log_product_action(base, 'CREATE',
                       f'从 {platform} 抓取商品 {item_id}', operator=creator)

    desc = data.get("group_description") or data.get("single_description", "")

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
        core_sku = ProductCore.objects.create(base=base,
                                              sku=generate_unique_sku(),
                                              p_name=p_name,
                                              UPC="",
                                              cost=cost if cost > 0 else 0,
                                              purchase_url="")
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
                              fixed_attributes=None):
    """
    Celery 异步抓取 eBay 商品。前端创建 FetchTask(PENDING) 后立即返回，
    后台异步完成抓取并更新 FetchTask 状态。
    """
    from productbase.models import FetchTask

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
            fixed_attributes=fixed_attributes)

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
                                          fixed_attributes=None):
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
                                       fixed_attributes=fixed_attributes)

    check_and_update_base_status([base_group.id])
    return base_group


# ======================
# 🔥 状态检查（已改新表）
# 图片上传 → productbase/image_hosting.py（独立模块，可切换服务商）



@app.task(bind=True, max_retries=3)
def migrate_images_to_cdn(self, base_id):
    """
    Celery 异步任务：将 BaseProductGroup 下所有 eBay 图片迁移到聚合图床。
    - 按 image_url 去重，同一 URL 只上传一次
    - 逐张上传，间隔 0.5s 避免限速
    - 单张失败重试 3 次（指数退避）
    - 成功后批量更新所有引用该 URL 的 ProductImage
    """
    from productbase.models import ProductImage, ProductGroup, ProductCore
    # Celery fork 子进程继承的数据库连接可能已失效，先关闭重建
    connection.close()

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
        return {'total': 0, 'migrated': 0, 'failed': 0}

    # 2. 按 URL 去重，构建 url → [image_ids] 映射
    url_map = {}
    for img in ebay_images:
        url_map.setdefault(img.image_url, []).append(img.id)

    unique_urls = list(url_map.keys())
    print(f'[CDN] Base {base_id}: {len(ebay_images)} images, '
          f'{len(unique_urls)} unique URLs to migrate')

    # 3. 逐个上传（去重后），间隔 0.5s
    migrated = 0
    failed = 0
    failed_urls = []
    url_replacements = {}  # old_url → new_url

    for i, old_url in enumerate(unique_urls):
        print(f'[CDN] [{i+1}/{len(unique_urls)}] Uploading: {old_url[:70]}...')
        new_url = upload_image(old_url)

        if new_url:
            url_replacements[old_url] = new_url
            migrated += 1
            print(f'[CDN] [{i+1}/{len(unique_urls)}] OK')
        else:
            failed += 1
            failed_urls.append(old_url)
            print(f'[CDN] [{i+1}/{len(unique_urls)}] FAILED')

        # 间隔 0.5s，避免限速（最后一张不等待）
        if i < len(unique_urls) - 1:
            time.sleep(0.5)

    # 4. 确保数据库连接干净，在事务中批量更新 image_url
    close_old_connections()
    updated_count = 0
    with transaction.atomic():
        for old_url, new_url in url_replacements.items():
            img_ids = url_map[old_url]
            ProductImage.objects.filter(id__in=img_ids).update(image_url=new_url)
            updated_count += len(img_ids)

    result = {
        'total': len(ebay_images),
        'unique_urls': len(unique_urls),
        'migrated': migrated,
        'failed': failed,
        'updated_records': updated_count
    }
    if failed_urls:
        result['failed_urls'] = failed_urls
    print(f'[CDN] Base {base_id} done: {result}')
    try:
        base = BaseProductGroup.objects.get(id=base_id)
        if result['migrated'] > 0 or result['failed'] > 0:
            m = result['migrated']
            f = result['failed']
            if f > 0:
                log_product_action(base, 'IMAGE_MIGRATE',
                                   f'图片迁移部分完成：{m}/{len(unique_urls)} 成功，{f} 失败。'
                                   f'失败 URL：{", ".join(failed_urls[:5])}')
            else:
                log_product_action(base, 'IMAGE_MIGRATE',
                                   f'迁移 {m} 张图片（{result["updated_records"]} 条记录更新）')
        # 无论有无迁移，都刷新状态
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

                # INIT→PREPARING 时异步触发图片迁移
                if was_init:
                    print(f'[CDN] Dispatching migration for base {base_id}')
                    migrate_images_to_cdn.delay(base_id)

        except Exception:
            continue
