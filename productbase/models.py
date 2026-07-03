from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()


def log_product_action(base_group, action, detail="", operator="system"):
    """记录产品操作日志"""
    ProductLog.objects.create(base_group=base_group,
                              action=action,
                              detail=detail,
                              operator=operator)


class BaseProductGroup(models.Model):
    """
    基础产品组模型
    存储产品公共顶层信息
    """
    p_status = models.CharField(max_length=30, verbose_name="产品状态")
    category = models.CharField(max_length=500,
                                blank=True,
                                verbose_name="产品类目")
    category_id = models.CharField(max_length=100,
                                   blank=True,
                                   verbose_name="类目ID路径")
    supplier = models.CharField(max_length=100, blank=True, verbose_name="供应商")
    series = models.CharField(max_length=100, blank=True, verbose_name="产品系列")
    tag = models.CharField(max_length=200, blank=True, verbose_name="标签")
    note = models.TextField(blank=True, verbose_name="备注")
    var_mappings = models.JSONField(default=dict,
                                    blank=True,
                                    verbose_name="变体值翻译映射")
    image_migrated = models.BooleanField(default=False,
                                         verbose_name="图片迁移完成")
    variant_mapped = models.BooleanField(default=False,
                                         verbose_name="变体映射完成")
    primary_variant = models.CharField(max_length=50,
                                       blank=True,
                                       verbose_name="主属性（控制图片切换）")
    from_item_id = models.CharField(max_length=50,
                                    null=True,
                                    blank=True,
                                    verbose_name="源id")
    from_platform = models.CharField(max_length=50,
                                     null=True,
                                     blank=True,
                                     verbose_name="源平台")
    from_site_id = models.CharField(max_length=50,
                                    null=True,
                                    blank=True,
                                    verbose_name="源站点")

    creator = models.CharField(max_length=50, verbose_name="创建人")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "基础产品组"
        verbose_name_plural = "基础产品组"
        ordering = ["-create_time"]

    def __str__(self):
        return f"基础产品_{self.id}"


class ProductGroup(models.Model):
    """
    店铺维度产品组
    """
    base = models.ForeignKey(BaseProductGroup,
                             on_delete=models.CASCADE,
                             related_name="product_groups",
                             verbose_name="关联基础产品组")

    shop_account = models.CharField(max_length=100, verbose_name="店铺账号")
    platform = models.CharField(max_length=50, verbose_name="所属平台")
    title = models.CharField(max_length=200, verbose_name="产品组标题")
    site = models.CharField(max_length=50,
                            null=True,
                            blank=True,
                            verbose_name="站点")
    p_status = models.CharField(max_length=30,
                                null=True,
                                blank=True,
                                verbose_name="产品状态")
    variant_name = models.CharField(max_length=200,
                                    blank=True,
                                    verbose_name="变体属性名称")
    is_main = models.BooleanField(default=False, verbose_name="是否主店铺")
    desc = models.TextField(blank=True, verbose_name="产品组描述")
    custom_attributes = models.JSONField(blank=True,
                                         null=True,
                                         verbose_name="自定义属性")
    listing_config = models.ForeignKey("ListingConfig",
                                      null=True,
                                      blank=True,
                                      on_delete=models.SET_NULL,
                                      related_name="linked_product_groups",
                                      verbose_name="关联刊登配置")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    shop_synced_at = models.DateTimeField(null=True,
                                          blank=True,
                                          verbose_name="上次同步时间")
    title_optimized = models.BooleanField(default=False,
                                           verbose_name="标题已优化")
    desc_optimized = models.BooleanField(default=False,
                                          verbose_name="描述已优化")

    class Meta:
        verbose_name = "店铺产品组"
        verbose_name_plural = "店铺产品组"
        ordering = ["-id"]

    def __str__(self):
        return self.title

    def get_variant_names(self):
        if not self.variant_name:
            return []
        return [v.strip() for v in self.variant_name.split(",")]

    def get_variant_count(self):
        return len(self.get_variant_names())

    def save(self, *args, **kwargs):
        if self.variant_name:
            name_list = [
                v.strip().lower() for v in self.variant_name.split(",")
            ]
            name_list = [item for item in name_list if item]
            self.variant_name = ",".join(name_list)
        # 过滤 4-byte emoji（MySQL utf8 不支持）
        from productbase.tasks import remove_emoji_special
        if self.desc:
            self.desc = remove_emoji_special(self.desc)
        if self.title:
            self.title = remove_emoji_special(self.title)
        super().save(*args, **kwargs)


# ===================== 新增：SKU核心数据表（全局唯一、永不重复） =====================
class ProductCore(models.Model):
    """
    SKU核心数据：全店铺共用，永久不变
    字段：sku、p_name、UPC、cost、purchase_url
    """
    base = models.ForeignKey(BaseProductGroup,
                             on_delete=models.CASCADE,
                             related_name="core_skus",
                             verbose_name="所属基础产品组")

    # 全局唯一编码
    sku = models.CharField(max_length=100, unique=True, verbose_name="SKU编码")
    p_name = models.CharField(max_length=200, verbose_name="产品名称")
    UPC = models.CharField(max_length=50, blank=True, verbose_name="UPC码")
    cost = models.DecimalField(max_digits=10,
                               decimal_places=2,
                               default=0,
                               verbose_name="成本")
    purchase_url = models.CharField(max_length=500,
                                    blank=True,
                                    verbose_name="采购链接")
    warehouse = models.CharField(max_length=100,
                                  blank=True,
                                  default='',
                                  verbose_name="仓库")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    sku_synced_at = models.DateTimeField(null=True,
                                         blank=True,
                                         verbose_name="上次同步时间")

    class Meta:
        verbose_name = "SKU核心数据"
        verbose_name_plural = "SKU核心数据"

    def __str__(self):
        return self.sku


# ===================== 改造原Product：店铺差异化数据表 =====================
class ProductShop(models.Model):
    """
    店铺维度SKU数据：多语言、多价格、多属性，每个店铺独立
    """
    # 关联店铺产品组
    group = models.ForeignKey(ProductGroup,
                              on_delete=models.CASCADE,
                              related_name="shop_skus",
                              verbose_name="所属店铺产品组")
    # 关联全局唯一的核心SKU
    core_sku = models.ForeignKey(ProductCore,
                                 on_delete=models.CASCADE,
                                 related_name="shop_records",
                                 verbose_name="关联核心SKU")

    # 店铺差异化：标题、描述、多语言属性
    title = models.CharField(max_length=200, verbose_name="变体标题")
    desc = models.TextField(blank=True, verbose_name="变体描述")

    # 店铺差异化：售价、币种
    price = models.DecimalField(max_digits=10,
                                decimal_places=2,
                                verbose_name="售价")
    currency = models.CharField(max_length=20, verbose_name="币种")

    # 多语言变体属性（不同国家/店铺可自定义）
    var1 = models.CharField(max_length=100, blank=True, verbose_name="变体属性值1")
    var2 = models.CharField(max_length=100, blank=True, verbose_name="变体属性值2")
    var3 = models.CharField(max_length=100, blank=True, verbose_name="变体属性值3")
    var4 = models.CharField(max_length=100, blank=True, verbose_name="变体属性值4")

    # 店铺自定义属性
    custom_attributes = models.JSONField(blank=True,
                                         null=True,
                                         verbose_name="自定义属性")

    def save(self, *args, **kwargs):
        from productbase.tasks import remove_emoji_special
        if self.title:
            self.title = remove_emoji_special(self.title)
        if self.desc:
            self.desc = remove_emoji_special(self.desc)
        super().save(*args, **kwargs)

    class Meta:
        # 联合唯一：一个店铺组下，同一个核心SKU 只允许一条记录
        unique_together = ("group", "core_sku")
        verbose_name = "店铺SKU数据"
        verbose_name_plural = "店铺SKU数据"

    def __str__(self):
        return f"{self.group.title} - {self.core_sku.sku}"


class ProductImage(models.Model):
    """
    产品图片：归属全局核心SKU（图片全店铺共用）
    """
    base_group = models.ForeignKey(BaseProductGroup,
                                   on_delete=models.CASCADE,
                                   null=True,
                                   blank=True,
                                   related_name="images",
                                   verbose_name="关联基础产品组")
    group = models.ForeignKey(ProductGroup,
                              on_delete=models.CASCADE,
                              null=True,
                              blank=True,
                              related_name="images",
                              verbose_name="关联店铺产品组")
    # 图片绑定核心SKU，全店铺共享
    product_core = models.ForeignKey(ProductCore,
                                     on_delete=models.CASCADE,
                                     null=True,
                                     blank=True,
                                     related_name="images",
                                     verbose_name="关联核心SKU")

    image_url = models.CharField(max_length=500, verbose_name="图片地址")
    sort = models.IntegerField(default=0, verbose_name="排序序号")
    is_cover = models.BooleanField(default=False, verbose_name="是否封面图")

    class Meta:
        verbose_name = "产品图片"
        verbose_name_plural = "产品图片"
        ordering = ["sort"]

    def __str__(self):
        return self.image_url


class FetchTask(models.Model):
    """
    抓取任务表（无改动）
    """
    STATUS_CHOICES = (
        ("PENDING", "待抓取"),
        ("PROCESSING", "抓取中"),
        ("SUCCESS", "已抓取"),
        ("FAILED", "异常"),
    )

    item_id = models.CharField(max_length=50, verbose_name="商品ID")
    marketplace_id = models.CharField(max_length=30, verbose_name="站点ID")
    platform = models.CharField(max_length=30,
                                default="EBAY",
                                verbose_name="平台")
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES,
                              default="PENDING",
                              verbose_name="任务状态")
    log = models.TextField(blank=True, verbose_name="任务日志")
    base_group = models.ForeignKey(BaseProductGroup,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True,
                                   verbose_name="关联基础产品组")
    creator = models.CharField(max_length=50,
                               default="system",
                               verbose_name="创建人")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "抓取任务"
        verbose_name_plural = "抓取任务"
        ordering = ["-create_time"]

    def __str__(self):
        return f"{self.item_id} | {self.get_status_display()}"


class Supplier(models.Model):
    """供应商"""
    name = models.CharField(max_length=200, unique=True, verbose_name="名称")
    is_favorite = models.BooleanField(default=False, verbose_name="是否收藏")
    purchase_channel = models.CharField(max_length=200,
                                        blank=True,
                                        verbose_name="采购渠道")
    link_url = models.CharField(max_length=500,
                                blank=True,
                                verbose_name="链接地址")
    contact_person = models.CharField(max_length=100,
                                      blank=True,
                                      verbose_name="联系人")
    phone = models.CharField(max_length=50, blank=True, verbose_name="电话")
    wechat = models.CharField(max_length=100, blank=True, verbose_name="微信")
    qq = models.CharField(max_length=50, blank=True, verbose_name="QQ")
    address = models.CharField(max_length=300, blank=True, verbose_name="地址")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "供应商"
        verbose_name_plural = "供应商"
        ordering = ["-create_time"]

    def __str__(self):
        return self.name


class ProductSeries(models.Model):
    """产品系列"""
    supplier = models.ForeignKey(Supplier,
                                 on_delete=models.CASCADE,
                                 related_name="series_list",
                                 verbose_name="供应商")
    name = models.CharField(max_length=200, verbose_name="名称")
    price = models.DecimalField(max_digits=10,
                                decimal_places=2,
                                default=0,
                                verbose_name="价格")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "产品系列"
        verbose_name_plural = "产品系列"
        ordering = ["-create_time"]

    def __str__(self):
        return f"{self.supplier.name} - {self.name}"


class ProductLog(models.Model):
    """产品操作日志"""
    ACTION_CHOICES = (
        ('CREATE', '创建产品'),
        ('UPDATE', '修改产品'),
        ('ADD_SHOP', '新增店铺'),
        ('DELETE_SHOP', '删除店铺'),
        ('ADD_SKU', '新增SKU'),
        ('DELETE_SKU', '删除SKU'),
        ('STATUS_CHANGE', '状态变更'),
        ('IMAGE_MIGRATE', '图片迁移完成'),
        ('OPTIMIZE_TITLE', '优化标题'),
        ('OPTIMIZE_DESC', '优化描述'),
        ('VARIANT', '变体映射'),
        ('PRICE_RULE', '定价规则'),
        ('WAREHOUSE', '仓库匹配'),
    )

    base_group = models.ForeignKey(BaseProductGroup,
                                   on_delete=models.SET_NULL,
                                   null=True,
                                   blank=True,
                                   related_name="logs",
                                   verbose_name="关联产品")
    action = models.CharField(max_length=20,
                              choices=ACTION_CHOICES,
                              verbose_name="操作类型")
    detail = models.TextField(blank=True, verbose_name="操作详情")
    operator = models.CharField(max_length=50, default="system", verbose_name="操作人")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")

    class Meta:
        verbose_name = "产品操作日志"
        verbose_name_plural = "产品操作日志"
        ordering = ["-create_time"]

    def __str__(self):
        return f"[{self.get_action_display()}] {self.base_group.id} @ {self.create_time}"


# ------------------------------------------------------------------------------
# 用户自定义配置
# ------------------------------------------------------------------------------

class PricingRule(models.Model):
    """定价规则 — 抓取时根据公式计算最终价格"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="pricing_rules",
                             verbose_name="所属用户")
    name = models.CharField(max_length=100, verbose_name="规则名称")
    formula = models.CharField(max_length=500, verbose_name="定价公式")
    min_price = models.DecimalField(max_digits=10,
                                    decimal_places=2,
                                    null=True,
                                    blank=True,
                                    verbose_name="最低限价")
    max_price = models.DecimalField(max_digits=10,
                                    decimal_places=2,
                                    null=True,
                                    blank=True,
                                    verbose_name="最高限价")
    creator = models.ForeignKey(User,
                                null=True,
                                on_delete=models.SET_NULL,
                                related_name="created_pricing_rules",
                                verbose_name="创建人")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "定价规则"
        verbose_name_plural = "定价规则"
        ordering = ["-create_time"]

    def __str__(self):
        return self.name


class ShopConfig(models.Model):
    """店铺配置 — 创建产品/抓取时引用"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="shop_configs",
                             verbose_name="所属用户")
    platform = models.CharField(max_length=50, verbose_name="平台")
    shop_account = models.CharField(max_length=100, verbose_name="店铺账号")
    site = models.CharField(max_length=50,
                           blank=True,
                           verbose_name="站点")
    is_main = models.BooleanField(default=False, verbose_name="是否主店铺")
    auto_create_shop = models.BooleanField(default=True,
                                           verbose_name="创建产品时自动创建店铺")

    listing_config = models.ForeignKey("ListingConfig",
                                       null=True,
                                       blank=True,
                                       on_delete=models.SET_NULL,
                                       related_name="shop_configs",
                                       verbose_name="刊登配置")

    pricing_rule = models.ForeignKey("PricingRule",
                                     null=True,
                                     blank=True,
                                     on_delete=models.SET_NULL,
                                     related_name="shop_configs",
                                     verbose_name="定价规则")

    creator = models.ForeignKey(User,
                                null=True,
                                on_delete=models.SET_NULL,
                                related_name="created_shop_configs",
                                verbose_name="创建人")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "店铺配置"
        verbose_name_plural = "店铺配置"
        ordering = ["-create_time"]
        unique_together = ('user', 'platform', 'shop_account', 'site')

    def __str__(self):
        return f"{self.platform} - {self.shop_account} ({'主' if self.is_main else '子'})"


class ListingConfig(models.Model):
    """刊登配置 — 被 ShopConfig 引用"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="listing_configs",
                             verbose_name="所属用户")
    name = models.CharField(max_length=100, verbose_name="配置名称")
    default_stock = models.IntegerField(default=0, verbose_name="默认在线初始库存")
    tags = models.CharField(max_length=500, blank=True, verbose_name="标签")

    listing_template = models.TextField(blank=True, verbose_name="通用刊登模板")
    payment_method = models.TextField(blank=True, verbose_name="付款方式")
    shipping_method = models.TextField(blank=True, verbose_name="货运方式")
    excluded_regions = models.TextField(blank=True, verbose_name="不运送地区")
    buyer_requirements = models.TextField(blank=True, verbose_name="买家要求")
    return_policy = models.TextField(blank=True, verbose_name="退货政策")
    item_location = models.CharField(max_length=200,
                                     blank=True,
                                     verbose_name="物品所在地")

    # 广告设置
    promoted_listing_enabled = models.BooleanField(default=False,
                                                   verbose_name="是否应用Promoted Listing")
    promoted_listing_ad_rate = models.DecimalField(max_digits=5,
                                                   decimal_places=2,
                                                   default=0,
                                                   verbose_name="Promoted Listing广告费率")
    campaign = models.TextField(blank=True, verbose_name="Campaign")
    sale_plan = models.TextField(blank=True, verbose_name="销售计划")
    discount = models.TextField(blank=True, verbose_name="折扣")

    match_shop_account = models.CharField(max_length=200,
                                          blank=True,
                                          verbose_name="匹配店铺账号")
    match_site = models.CharField(max_length=100,
                                  blank=True,
                                  verbose_name="匹配站点")

    creator = models.ForeignKey(User,
                                null=True,
                                on_delete=models.SET_NULL,
                                verbose_name="创建人")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "刊登配置"
        verbose_name_plural = "刊登配置"
        ordering = ["-create_time"]

    def __str__(self):
        return self.name


class FetchConfig(models.Model):
    """抓取配置 — 每用户仅一套启用"""
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="fetch_configs",
                             verbose_name="所属用户")
    name = models.CharField(max_length=100, verbose_name="配置名称")
    is_active = models.BooleanField(default=False, verbose_name="是否启用")
    keep_attributes = models.JSONField(default=list,
                                       verbose_name="属性保留白名单")
    fixed_attributes = models.JSONField(default=dict,
                                        verbose_name="固定附加属性")

    creator = models.ForeignKey(User,
                                null=True,
                                on_delete=models.SET_NULL,
                                verbose_name="创建人")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "抓取配置"
        verbose_name_plural = "抓取配置"
        ordering = ["-create_time"]
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(is_active=True),
                name='unique_active_fetch_config_per_user'),
        ]

    def __str__(self):
        return f"{self.name} {'✓' if self.is_active else ''}"


class DifyUsageLog(models.Model):
    """Dify AI 调用消耗记录"""
    user = models.ForeignKey(User,
                              on_delete=models.CASCADE,
                              related_name="dify_usage_logs",
                              verbose_name="调用用户")
    product_group = models.ForeignKey(ProductGroup,
                                       on_delete=models.SET_NULL,
                                       null=True,
                                       blank=True,
                                       related_name="dify_usage_logs",
                                       verbose_name="关联店铺")
    optimize_type = models.CharField(max_length=20, verbose_name="优化类型")
    prompt_tokens = models.IntegerField(default=0, verbose_name="提示词 Token")
    completion_tokens = models.IntegerField(default=0, verbose_name="生成 Token")
    total_tokens = models.IntegerField(default=0, verbose_name="总 Token")
    total_price = models.DecimalField(max_digits=10,
                                       decimal_places=6,
                                       default=0,
                                       verbose_name="费用(RMB)")
    currency = models.CharField(max_length=10,
                                 default="RMB",
                                 verbose_name="币种")
    latency = models.FloatField(default=0, verbose_name="延迟(秒)")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "Dify 调用记录"
        verbose_name_plural = "Dify 调用记录"
        ordering = ["-create_time"]

    def __str__(self):
        return f"[{self.optimize_type}] {self.total_tokens} tokens ¥{self.total_price}"


# ------------------------------------------------------------------------------
# 变体映射（多用户共享）
# ------------------------------------------------------------------------------
class VariantMappingAttribute(models.Model):
    """变体属性名 — 匹配产品的变体维度（如 color）"""
    attribute_name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="变体属性名",
        help_text="属性名，多个用逗号分隔为 OR 关系。如: color,colour")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "变体映射属性"
        verbose_name_plural = verbose_name
        ordering = ["attribute_name"]

    def __str__(self):
        return self.attribute_name


class VariantMappingValue(models.Model):
    """变体值替换规则 — 匹配模式 → 替换值（部分替换）"""
    attribute = models.ForeignKey(
        VariantMappingAttribute,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name="所属属性")
    match_pattern = models.CharField(
        max_length=200,
        verbose_name="匹配模式",
        help_text="待匹配的前缀文本，如: For Samsung")
    replace_value = models.CharField(
        max_length=200,
        verbose_name="替换值",
        help_text="匹配后替换为的值，如: 三星")
    priority = models.IntegerField(
        default=0,
        verbose_name="优先级",
        help_text="数值越大越优先匹配。同属性下长模式应设置更高优先级")

    class Meta:
        verbose_name = "变体映射值"
        verbose_name_plural = verbose_name
        unique_together = ("attribute", "match_pattern")
        ordering = ["-priority"]

    def __str__(self):
        return f"{self.match_pattern} → {self.replace_value}"


# ------------------------------------------------------------------------------
# 仓库匹配配置（多用户共享）
# ------------------------------------------------------------------------------
class WarehouseConfig(models.Model):
    """仓库匹配规则 — 根据类目匹配仓库，全用户共享"""
    category_id = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="类目ID",
        help_text="前缀匹配 eBay categoryIdPath，如: 15032 可匹配 15032|9394|20349")
    category_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="类目名称",
        help_text="子串匹配 categoryPath（大小写不敏感），如: Cases")
    warehouse = models.CharField(
        max_length=100,
        verbose_name="仓库名称",
        help_text="匹配到的仓库，如: F仓、华强仓")
    priority = models.IntegerField(
        default=0,
        verbose_name="优先级",
        help_text="数值越大越优先匹配")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "仓库匹配配置"
        verbose_name_plural = verbose_name
        ordering = ["-priority", "-create_time"]

    def __str__(self):
        label = self.category_id or self.category_name or "默认"
        return f"{label} → {self.warehouse}"


class ImageStatsCache(models.Model):
    """图片统计缓存 — 由 Celery 异步更新，接口只读缓存"""
    cdn_total = models.IntegerField(default=0, verbose_name="CDN 总数")
    db_total = models.IntegerField(default=0, verbose_name="DB 总数")
    migrated = models.IntegerField(default=0, verbose_name="已迁移")
    unmigrated = models.IntegerField(default=0, verbose_name="未迁移")
    orphan = models.IntegerField(default=0, verbose_name="孤儿数")
    computing = models.BooleanField(default=False, verbose_name="计算中")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "图片统计缓存"
        verbose_name_plural = verbose_name
