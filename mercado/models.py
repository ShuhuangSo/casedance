from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class Listing(models.Model):
    """
    在线产品
    """

    item_id = models.CharField(max_length=20, verbose_name='商品id', help_text='商品id')
    site_id = models.CharField(max_length=10, verbose_name='站点id', help_text='站点id')
    title = models.CharField(max_length=150, verbose_name='商品名称', help_text='商品名称')
    image = models.CharField(null=True, blank=True, max_length=200, verbose_name='主图链接', help_text='主图链接')
    link = models.CharField(null=True, blank=True, max_length=200, verbose_name='商品链接', help_text='商品链接')
    price = models.FloatField(null=True, blank=True, verbose_name='销售定价', help_text='销售定价')
    currency = models.CharField(null=True, blank=True, max_length=5, verbose_name='币种', help_text='币种')
    total_sold = models.IntegerField(default=0, null=True, blank=True, verbose_name='总销量', help_text='总销量')
    sold_7d = models.IntegerField(default=0, null=True, blank=True, verbose_name='近7天销量', help_text='近7天销量')
    sold_30d = models.IntegerField(default=0, null=True, blank=True, verbose_name='近30天销量', help_text='近30天销量')
    reviews = models.IntegerField(default=0, null=True, blank=True, verbose_name='评论数量', help_text='评论数量')
    rating_average = models.FloatField(null=True, blank=True, verbose_name='评分', help_text='评分')
    start_date = models.DateField(null=True, verbose_name='上架时间', help_text='上架时间')
    listing_status = models.CharField(null=True, blank=True, max_length=10, verbose_name='商品状态', help_text='商品状态')
    health = models.FloatField(null=True, blank=True, verbose_name='健康度', help_text='健康度')
    stock_num = models.IntegerField(default=0, null=True, blank=True, verbose_name='库存数', help_text='库存数')
    ship_type = models.CharField(null=True, blank=True, max_length=20, verbose_name='物流类型', help_text='物流类型')
    is_cbt = models.BooleanField(default=True, verbose_name='是否大陆卖家', help_text='是否大陆卖家')
    is_free_shipping = models.BooleanField(default=True, verbose_name='是否免运费', help_text='是否免运费')
    seller_id = models.CharField(null=True, blank=True, max_length=20, verbose_name='卖家id', help_text='卖家id')
    seller_name = models.CharField(null=True, blank=True, max_length=50, verbose_name='卖家名称', help_text='卖家名称')
    brand = models.CharField(null=True, blank=True, max_length=20, verbose_name='品牌名称', help_text='品牌名称')
    collection = models.BooleanField(default=False, verbose_name='是否收藏', help_text='是否收藏')
    cost = models.FloatField(null=True, blank=True, verbose_name='商品成本', help_text='商品成本')
    profit = models.FloatField(null=True, blank=True, verbose_name='利润', help_text='利润')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    update_time = models.DateTimeField(null=True, verbose_name='数据更新时间', help_text='数据更新时间')

    class Meta:
        verbose_name = '在线产品'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.item_id


class ListingTrack(models.Model):
    """
    商品跟踪
    """

    listing = models.ForeignKey(Listing, related_name='listing_track', on_delete=models.CASCADE, verbose_name='在线产品',
                                help_text='在线产品')
    currency = models.CharField(null=True, blank=True, max_length=5, verbose_name='币种', help_text='币种')
    price = models.FloatField(default=0, null=True, blank=True, verbose_name='销售定价', help_text='销售定价')
    total_sold = models.IntegerField(default=0, null=True, blank=True, verbose_name='总销量', help_text='总销量')
    today_sold = models.IntegerField(default=0, null=True, blank=True, verbose_name='今天销量', help_text='今天销量')
    reviews = models.IntegerField(default=0, null=True, blank=True, verbose_name='评论数量', help_text='评论数量')
    rating_average = models.FloatField(null=True, blank=True, verbose_name='评分', help_text='评分')
    health = models.FloatField(null=True, blank=True, verbose_name='健康度', help_text='健康度')
    stock_num = models.IntegerField(default=0, null=True, blank=True, verbose_name='库存数', help_text='库存数')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '商品跟踪'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return str(self.listing)


class Seller(models.Model):
    """
    卖家
    """

    seller_id = models.CharField(max_length=10, verbose_name='卖家id', help_text='卖家id')
    site_id = models.CharField(max_length=10, verbose_name='站点id', help_text='站点id')
    nickname = models.CharField(max_length=50, verbose_name='卖家名称', help_text='卖家名称')
    level_id = models.CharField(max_length=30, verbose_name='信誉水平', help_text='信誉水平')
    total = models.IntegerField(default=0, null=True, blank=True, verbose_name='总订单', help_text='总订单')
    canceled = models.IntegerField(default=0, null=True, blank=True, verbose_name='取消订单', help_text='取消订单')
    negative = models.FloatField(null=True, blank=True, verbose_name='差评率', help_text='差评率')
    neutral = models.FloatField(null=True, blank=True, verbose_name='中评率', help_text='中评率')
    positive = models.FloatField(null=True, blank=True, verbose_name='好评率', help_text='好评率')
    registration_date = models.DateField(null=True, verbose_name='注册日期', help_text='注册日期')
    link = models.CharField(null=True, blank=True, max_length=200, verbose_name='店铺链接', help_text='店铺链接')
    sold_60d = models.IntegerField(default=0, null=True, blank=True, verbose_name='60天销量', help_text='60天销量')
    total_items = models.IntegerField(default=0, null=True, blank=True, verbose_name='listing数量', help_text='listing数量')
    collection = models.BooleanField(default=False, verbose_name='是否收藏', help_text='是否收藏')
    update_time = models.DateTimeField(null=True, verbose_name='更新时间', help_text='更新时间')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')

    class Meta:
        verbose_name = '卖家'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.nickname


class SellerTrack(models.Model):
    """
    卖家跟踪
    """

    seller = models.ForeignKey(Seller, related_name='seller_track', on_delete=models.CASCADE, verbose_name='卖家',
                               help_text='卖家')
    total = models.IntegerField(default=0, null=True, blank=True, verbose_name='总订单', help_text='总订单')
    today_sold = models.IntegerField(default=0, null=True, blank=True, verbose_name='今天订单', help_text='今天订单')
    negative = models.FloatField(null=True, blank=True, verbose_name='差评率', help_text='差评率')
    neutral = models.FloatField(null=True, blank=True, verbose_name='中评率', help_text='中评率')
    positive = models.FloatField(null=True, blank=True, verbose_name='好评率', help_text='好评率')
    total_items = models.IntegerField(default=0, null=True, blank=True, verbose_name='listing数量', help_text='listing数量')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '卖家跟踪'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return str(self.seller)


class Categories(models.Model):
    """
    站点类目
    """

    categ_id = models.CharField(max_length=10, verbose_name='类目id', help_text='类目id')
    father_id = models.CharField(null=True, max_length=10, verbose_name='父类目id', help_text='父类目id')
    site_id = models.CharField(max_length=10, verbose_name='站点id', help_text='站点id')
    name = models.CharField(null=True, max_length=100, verbose_name='类目名称', help_text='类目名称')
    t_name = models.CharField(null=True, blank=True, max_length=100, verbose_name='翻译类目名称', help_text='翻译类目名称')
    path_from_root = models.CharField(max_length=200, verbose_name='类目导航', help_text='类目导航')
    total_items = models.IntegerField(default=0, null=True, blank=True, verbose_name='类目产品数量', help_text='类目产品数量')
    has_children = models.BooleanField(default=True, verbose_name='是否有子类目', help_text='是否有子类目')
    collection = models.BooleanField(default=False, verbose_name='是否收藏', help_text='是否收藏')
    update_time = models.DateTimeField(null=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '站点类目'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.name


class Keywords(models.Model):
    """
    关键词
    """

    categ_id = models.CharField(max_length=10, verbose_name='类目id', help_text='类目id')
    keyword = models.CharField(null=True, max_length=100, verbose_name='关键词', help_text='关键词')
    t_keyword = models.CharField(null=True, blank=True, max_length=100, verbose_name='关键词翻译', help_text='关键词翻译')
    url = models.CharField(null=True, blank=True, max_length=200, verbose_name='url', help_text='url')
    rank = models.IntegerField(default=0, null=True, blank=True, verbose_name='排名', help_text='排名')
    status = models.CharField(null=True, blank=True, max_length=5, verbose_name='状态', help_text='状态')
    rank_changed = models.IntegerField(default=0, null=True, blank=True, verbose_name='排名变化', help_text='排名变化')
    update_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '关键词'
        verbose_name_plural = verbose_name
        ordering = ['rank']

    def __str__(self):
        return self.keyword


class ApiSetting(models.Model):
    """
    api设置
    """

    access_token = models.CharField(max_length=50, verbose_name='api-token', help_text='api-token')

    class Meta:
        verbose_name = 'api设置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.access_token


class TransApiSetting(models.Model):
    """
    百度翻译api设置
    """

    appid = models.CharField(max_length=50, verbose_name='appid', help_text='appid')
    secretKey = models.CharField(max_length=50, verbose_name='secretKey', help_text='secretKey')

    class Meta:
        verbose_name = '百度翻译api设置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.appid


class MLProduct(models.Model):
    """
    mercado产品库
    """
    PRODUCT_STATUS = (
        ('ON_SALE', '在售'),
        ('OFFLINE', '停售'),
        ('CLEAN', '清仓中'),
    )

    sku = models.CharField(max_length=30, verbose_name='产品SKU', help_text='产品SKU')
    p_name = models.CharField(max_length=80, verbose_name='产品名称', help_text='产品名称')
    label_code = models.CharField(max_length=30, null=True, blank=True, verbose_name='FBM条码', help_text='FBM条码')
    upc = models.CharField(max_length=30, null=True, blank=True, verbose_name='UPC', help_text='UPC')
    item_id = models.CharField(max_length=30, null=True, blank=True, verbose_name='链接编号', help_text='链接编号')
    image = models.ImageField(null=True, blank=True, upload_to='ml_product', max_length=200, verbose_name='产品图片',
                              help_text='产品图片')
    p_status = models.CharField(max_length=10, choices=PRODUCT_STATUS, default='ON_SALE', verbose_name='产品状态',
                                help_text='产品状态')
    custom_code = models.CharField(null=True, blank=True, max_length=20, verbose_name='海关编码', help_text='海关编码')
    cn_name = models.CharField(null=True, blank=True, max_length=30, verbose_name='中文品名', help_text='中文品名')
    en_name = models.CharField(null=True, blank=True, max_length=30, verbose_name='英文品名', help_text='英文品名')
    brand = models.CharField(null=True, blank=True, max_length=20, verbose_name='品牌', help_text='品牌')
    declared_value = models.FloatField(null=True, blank=True, max_length=30, verbose_name='申报价值USD',
                                       help_text='申报价值USD')
    cn_material = models.CharField(null=True, blank=True, max_length=30, verbose_name='中文材质', help_text='中文材质')
    en_material = models.CharField(null=True, blank=True, max_length=30, verbose_name='英文材质', help_text='英文材质')
    use = models.CharField(null=True, blank=True, max_length=50, verbose_name='用途', help_text='用途')
    site = models.CharField(null=True, blank=True, max_length=30, verbose_name='站点', help_text='站点')
    shop = models.CharField(null=True, blank=True, max_length=50, verbose_name='上架店铺', help_text='上架店铺')

    unit_cost = models.FloatField(null=True, blank=True, verbose_name='成本价', help_text='成本价')
    first_ship_cost = models.FloatField(null=True, blank=True, verbose_name='预估头程运费', help_text='预估头程运费')
    length = models.FloatField(null=True, blank=True, verbose_name='长cm', help_text='长cm')
    width = models.FloatField(null=True, blank=True, verbose_name='宽cm', help_text='宽cm')
    heigth = models.FloatField(null=True, blank=True, verbose_name='高cm', help_text='高cm')
    weight = models.FloatField(null=True, blank=True, verbose_name='重量kg', help_text='重量kg')
    buy_url = models.CharField(null=True, blank=True, max_length=500, verbose_name='产品采购链接', help_text='产品采购链接')
    sale_url = models.CharField(null=True, blank=True, max_length=500, verbose_name='销售链接', help_text='销售链接')
    refer_url = models.CharField(null=True, blank=True, max_length=500, verbose_name='参考链接', help_text='参考链接')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    is_checked = models.BooleanField(default=False, null=True, verbose_name='是否核对', help_text='是否核对')
    label_title = models.CharField(null=True, blank=True, max_length=100, verbose_name='链接标题', help_text='链接标题')
    label_option = models.CharField(null=True, blank=True, max_length=50, verbose_name='链接选项', help_text='链接选项')
    packing_id = models.IntegerField(null=True, blank=True, verbose_name='包材id', help_text='包材id')
    buy_url2 = models.CharField(null=True, blank=True, max_length=500, verbose_name='产品采购链接2', help_text='产品采购链接2')
    buy_url3 = models.CharField(null=True, blank=True, max_length=500, verbose_name='产品采购链接3', help_text='产品采购链接3')
    buy_url4 = models.CharField(null=True, blank=True, max_length=500, verbose_name='产品采购链接4', help_text='产品采购链接4')
    buy_url5 = models.CharField(null=True, blank=True, max_length=500, verbose_name='产品采购链接5', help_text='产品采购链接5')

    class Meta:
        verbose_name = 'ML产品库'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.sku


class Packing(models.Model):
    """
    包材管理
    """

    name = models.CharField(max_length=80, verbose_name='包材名称', help_text='包材名称')
    size = models.CharField(max_length=80, verbose_name='尺寸', help_text='尺寸')
    weight = models.FloatField(default=0, null=True, blank=True, verbose_name='重量g', help_text='重量g')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '包材管理'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return self.name


class Shop(models.Model):
    """
    FBM店铺
    """

    warehouse_type = models.CharField(max_length=30, verbose_name='仓库类型', help_text='仓库类型')
    name = models.CharField(max_length=30, verbose_name='店铺代号', help_text='店铺代号')
    shop_type = models.CharField(max_length=30, null=True, blank=True, verbose_name='店铺类型', help_text='店铺类型')
    seller_id = models.CharField(max_length=30, null=True, blank=True, verbose_name='店铺ID', help_text='店铺ID')
    nickname = models.CharField(max_length=50, null=True, blank=True, verbose_name='店铺名称', help_text='店铺名称')
    site = models.CharField(max_length=20, null=True, blank=True, verbose_name='站点', help_text='站点')
    currency = models.CharField(max_length=10, null=True, blank=True, verbose_name='币种', help_text='币种')
    url = models.CharField(null=True, blank=True, max_length=300, verbose_name='店铺链接', help_text='店铺链接')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='是否启用', help_text='是否启用')
    total_profit = models.FloatField(null=True, blank=True, verbose_name='累计利润', help_text='累计利润')
    total_weight = models.FloatField(null=True, blank=True, verbose_name='库存总重量kg', help_text='库存总重量kg')
    total_cbm = models.FloatField(null=True, blank=True, verbose_name='库存总体积cbm', help_text='库存总体积cbm')
    stock_value = models.FloatField(null=True, blank=True, verbose_name='库存价值rmb', help_text='库存价值rmb')
    total_qty = models.IntegerField(null=True, blank=True, verbose_name='库存价值rmb', help_text='库存价值rmb')
    user = models.ForeignKey(User, related_name='user_shop', on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='user', help_text='user')
    name_color = models.CharField(max_length=20, null=True, blank=True, verbose_name='店铺名称颜色', help_text='店铺名称颜色')

    class Meta:
        verbose_name = 'FBM店铺'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.name


class ShopStock(models.Model):
    """
    店铺库存
    """
    PRODUCT_STATUS = (
        ('NORMAL', '普通'),
        ('HOT_SALE', '热卖'),
        ('OFFLINE', '停售'),
        ('CLEAN', '清仓中'),
    )

    shop = models.ForeignKey(Shop, related_name='shop_shopstock', on_delete=models.CASCADE, verbose_name='上架店铺',
                             help_text='上架店铺')
    sku = models.CharField(max_length=30, verbose_name='产品SKU', help_text='产品SKU')
    p_name = models.CharField(max_length=80, verbose_name='产品名称', help_text='产品名称')
    label_code = models.CharField(max_length=30, null=True, blank=True, verbose_name='FBM条码', help_text='FBM条码')
    upc = models.CharField(max_length=30, null=True, blank=True, verbose_name='UPC', help_text='UPC')
    item_id = models.CharField(max_length=30, null=True, blank=True, verbose_name='链接编号', help_text='链接编号')
    image = models.ImageField(null=True, blank=True, upload_to='ml_product', max_length=200, verbose_name='产品图片',
                              help_text='产品图片')
    p_status = models.CharField(max_length=10, choices=PRODUCT_STATUS, default='NORMAL', verbose_name='产品状态',
                                help_text='产品状态')
    qty = models.IntegerField(default=0, verbose_name='库存数量', help_text='库存数量')
    onway_qty = models.IntegerField(default=0, verbose_name='在途数量', help_text='在途数量')
    trans_qty = models.IntegerField(default=0, verbose_name='中转仓数量', help_text='中转仓数量')
    day15_sold = models.IntegerField(default=0, verbose_name='15天销量', help_text='15天销量')
    day30_sold = models.IntegerField(default=0, verbose_name='30天销量', help_text='30天销量')
    total_sold = models.IntegerField(default=0, verbose_name='累计销量', help_text='累计销量')
    unit_cost = models.FloatField(null=True, default=0, verbose_name='均摊成本价', help_text='均摊成本价')
    first_ship_cost = models.FloatField(null=True, default=0, verbose_name='均摊头程运费', help_text='均摊头程运费')
    length = models.FloatField(null=True, blank=True, verbose_name='长cm', help_text='长cm')
    width = models.FloatField(null=True, blank=True, verbose_name='宽cm', help_text='宽cm')
    heigth = models.FloatField(null=True, blank=True, verbose_name='高cm', help_text='高cm')
    weight = models.FloatField(null=True, blank=True, verbose_name='重量kg', help_text='重量kg')
    total_profit = models.FloatField(null=True, blank=True, verbose_name='累计利润', help_text='累计利润')
    total_weight = models.FloatField(null=True, blank=True, verbose_name='总重量kg', help_text='总重量kg')
    total_cbm = models.FloatField(null=True, blank=True, verbose_name='总体积cbm', help_text='总体积cbm')
    stock_value = models.FloatField(null=True, blank=True, verbose_name='库存价值rmb', help_text='库存价值rmb')
    refund_rate = models.FloatField(null=True, blank=True, verbose_name='退款率', help_text='退款率')
    avg_profit = models.FloatField(null=True, blank=True, verbose_name='平均毛利润', help_text='平均毛利润')
    avg_profit_rate = models.FloatField(null=True, blank=True, verbose_name='平均毛利率', help_text='平均毛利率')
    sale_url = models.CharField(null=True, blank=True, max_length=500, verbose_name='销售链接', help_text='销售链接')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='是否启用', help_text='是否启用')
    is_collect = models.BooleanField(default=True, verbose_name='是否收藏', help_text='是否收藏')

    class Meta:
        verbose_name = '店铺库存'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.sku


class TransStock(models.Model):
    """
    中转仓库存
    """
    shop = models.ForeignKey(Shop, related_name='shop_trans_stock', on_delete=models.CASCADE, verbose_name='所属中转仓',
                             help_text='所属中转仓')
    listing_shop = models.CharField(max_length=60, null=True, blank=True, verbose_name='上架店铺', help_text='上架店铺')
    sku = models.CharField(max_length=30, verbose_name='产品SKU', help_text='产品SKU')
    p_name = models.CharField(max_length=80, verbose_name='产品名称', help_text='产品名称')
    label_code = models.CharField(max_length=30, null=True, blank=True, verbose_name='FBM条码', help_text='FBM条码')
    upc = models.CharField(max_length=30, null=True, blank=True, verbose_name='UPC', help_text='UPC')
    item_id = models.CharField(max_length=30, null=True, blank=True, verbose_name='链接编号', help_text='链接编号')
    image = models.ImageField(null=True, blank=True, upload_to='ml_product', max_length=200, verbose_name='产品图片',
                              help_text='产品图片')
    qty = models.IntegerField(default=0, verbose_name='库存数量', help_text='库存数量')
    unit_cost = models.FloatField(null=True, default=0, verbose_name='均摊成本价', help_text='均摊成本价')
    first_ship_cost = models.FloatField(null=True, default=0, verbose_name='均摊头程运费', help_text='均摊头程运费')
    s_number = models.CharField(max_length=30, null=True, blank=True, verbose_name='运单编号', help_text='运单编号')
    batch = models.CharField(max_length=30, null=True, blank=True, verbose_name='批次号', help_text='批次号')
    box_number = models.CharField(max_length=30, verbose_name='箱号', help_text='箱号')
    carrier_box_number = models.CharField(max_length=30, null=True, blank=True, verbose_name='物流商箱唛号',
                                          help_text='物流商箱唛号')
    box_length = models.FloatField(null=True, blank=True, verbose_name='长cm', help_text='长cm')
    box_width = models.FloatField(null=True, blank=True, verbose_name='宽cm', help_text='宽cm')
    box_heigth = models.FloatField(null=True, blank=True, verbose_name='高cm', help_text='高cm')
    box_weight = models.FloatField(null=True, blank=True, verbose_name='重量kg', help_text='重量kg')
    box_cbm = models.FloatField(null=True, blank=True, verbose_name='体积cbm', help_text='体积cbm')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    arrived_date = models.DateField(null=True, blank=True, verbose_name='到仓日期', help_text='到仓日期')
    is_out = models.BooleanField(default=False, verbose_name='是否已出仓', help_text='是否已出仓')

    class Meta:
        verbose_name = '中转仓库存'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.sku


class Ship(models.Model):
    """
    头程运单
    """
    SHIP_STATUS = (
        ('PREPARING', '备货中'),
        ('SHIPPED', '已发货'),
        ('BOOKED', '已预约'),
        ('FINISHED', '已完成'),
        ('ERROR', '异常'),
    )

    s_number = models.CharField(max_length=30, null=True, blank=True, verbose_name='运单编号', help_text='运单编号')
    batch = models.CharField(max_length=30, null=True, blank=True, verbose_name='批次号', help_text='批次号')
    s_status = models.CharField(max_length=10, choices=SHIP_STATUS, default='PREPARING', verbose_name='产品状态',
                                help_text='产品状态')
    shop = models.CharField(max_length=30, null=True, blank=True, verbose_name='目标店铺', help_text='目标店铺')
    target = models.CharField(max_length=30, null=True, blank=True, verbose_name='目标入仓FBM/中转仓', help_text='目标入仓FBM/中转仓')
    fbm_warehouse = models.CharField(max_length=30, null=True, blank=True, verbose_name='fbm仓库', help_text='fbm仓库')
    envio_number = models.CharField(max_length=30, null=True, blank=True, verbose_name='Envio号', help_text='Envio号')
    send_from = models.CharField(max_length=30, null=True, blank=True, verbose_name='从哪发', help_text='从哪发')
    ship_type = models.CharField(max_length=10, null=True, blank=True, verbose_name='运单类型', help_text='运单类型')
    shipping_fee = models.FloatField(null=True, default=0, verbose_name='运费', help_text='运费')
    extra_fee = models.FloatField(null=True, default=0, verbose_name='额外费用', help_text='额外费用')
    carrier = models.CharField(max_length=30, null=True, blank=True, verbose_name='承运商', help_text='承运商')
    end_date = models.DateField(null=True, blank=True, verbose_name='物流截单日期', help_text='物流截单日期')
    ship_date = models.DateField(null=True, blank=True, verbose_name='航班日期', help_text='航班日期')
    book_date = models.DateField(null=True, blank=True, verbose_name='FBM预约日期', help_text='FBM预约日期')
    total_box = models.IntegerField(default=0, verbose_name='总箱数', help_text='总箱数')
    total_qty = models.IntegerField(default=0, verbose_name='总数量', help_text='总数量')
    weight = models.FloatField(null=True, blank=True, verbose_name='总重量kg', help_text='总重量kg')
    cbm = models.FloatField(null=True, blank=True, verbose_name='总体积cbm', help_text='总体积cbm')
    tag_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='标签名称', help_text='标签名称')
    tag_color = models.CharField(max_length=20, null=True, blank=True, verbose_name='标签颜色', help_text='标签颜色')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '头程运单'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.batch


class ShipDetail(models.Model):
    """
    运单详情
    """
    ship = models.ForeignKey(Ship, related_name='ship_shipDetail', on_delete=models.CASCADE, verbose_name='所属运单',
                             help_text='所属运单')
    target_FBM = models.CharField(max_length=30, null=True, blank=True, verbose_name='目标FBM仓库', help_text='目标FBM仓库')
    box_number = models.CharField(max_length=30, verbose_name='箱号', help_text='箱号')
    s_type = models.CharField(max_length=10, verbose_name='发货类型', help_text='发货类型')
    sku = models.CharField(max_length=30, verbose_name='产品SKU', help_text='产品SKU')
    p_name = models.CharField(max_length=80, verbose_name='产品名称', help_text='产品名称')
    label_code = models.CharField(max_length=30, null=True, blank=True, verbose_name='FBM条码', help_text='FBM条码')
    upc = models.CharField(max_length=30, null=True, blank=True, verbose_name='UPC', help_text='UPC')
    item_id = models.CharField(max_length=30, null=True, blank=True, verbose_name='链接编号', help_text='链接编号')
    image = models.ImageField(null=True, blank=True, upload_to='ml_product', max_length=200, verbose_name='产品图片',
                              help_text='产品图片')
    custom_code = models.CharField(null=True, blank=True, max_length=20, verbose_name='海关编码', help_text='海关编码')
    cn_name = models.CharField(null=True, blank=True, max_length=30, verbose_name='中文品名', help_text='中文品名')
    en_name = models.CharField(null=True, blank=True, max_length=30, verbose_name='英文品名', help_text='英文品名')
    brand = models.CharField(null=True, blank=True, max_length=20, verbose_name='品牌', help_text='品牌')
    declared_value = models.FloatField(null=True, blank=True, max_length=30, verbose_name='申报价值USD',
                                       help_text='申报价值USD')
    cn_material = models.CharField(null=True, blank=True, max_length=30, verbose_name='中文材质', help_text='中文材质')
    en_material = models.CharField(null=True, blank=True, max_length=30, verbose_name='英文材质', help_text='英文材质')
    use = models.CharField(null=True, blank=True, max_length=50, verbose_name='用途', help_text='用途')
    unit_cost = models.FloatField(null=True, default=0, verbose_name='成本价', help_text='成本价')
    avg_ship_fee = models.FloatField(null=True, default=0, verbose_name='单个分摊运费', help_text='单个分摊运费')
    qty = models.IntegerField(default=0, verbose_name='数量', help_text='数量')
    length = models.FloatField(null=True, blank=True, verbose_name='长cm', help_text='长cm')
    width = models.FloatField(null=True, blank=True, verbose_name='宽cm', help_text='宽cm')
    heigth = models.FloatField(null=True, blank=True, verbose_name='高cm', help_text='高cm')
    weight = models.FloatField(null=True, blank=True, verbose_name='重量kg', help_text='重量kg')
    note = models.CharField(max_length=300, null=True, blank=True, verbose_name='短备注', help_text='短备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    packing_name = models.CharField(null=True, blank=True, max_length=80, verbose_name='包材名称', help_text='包材名称')
    packing_size = models.CharField(null=True, blank=True, max_length=80, verbose_name='包材尺寸', help_text='包材尺寸')

    class Meta:
        verbose_name = '运单详情'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.sku


class ShipBox(models.Model):
    """
    包装箱
    """
    ship = models.ForeignKey(Ship, related_name='ship_shipBox', on_delete=models.CASCADE, verbose_name='所属运单',
                             help_text='所属运单')
    box_number = models.CharField(max_length=30, verbose_name='箱号', help_text='箱号')
    carrier_box_number = models.CharField(max_length=30, null=True, blank=True, verbose_name='物流商箱唛号',
                                          help_text='物流商箱唛号')
    item_qty = models.IntegerField(default=0, verbose_name='箱内产品数量', help_text='箱内产品数量')
    length = models.FloatField(null=True, blank=True, verbose_name='长cm', help_text='长cm')
    width = models.FloatField(null=True, blank=True, verbose_name='宽cm', help_text='宽cm')
    heigth = models.FloatField(null=True, blank=True, verbose_name='高cm', help_text='高cm')
    weight = models.FloatField(null=True, blank=True, verbose_name='重量kg', help_text='重量kg')
    cbm = models.FloatField(null=True, blank=True, verbose_name='体积cbm', help_text='体积cbm')
    size_weight = models.FloatField(null=True, blank=True, verbose_name='体积重kg', help_text='体积重kg')
    note = models.CharField(max_length=300, null=True, blank=True, verbose_name='短备注', help_text='短备注')

    class Meta:
        verbose_name = '包装箱'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.box_number


class Carrier(models.Model):
    """
    物流商
    """

    od_num = models.IntegerField(default=1, verbose_name='排序号', help_text='排序号')
    name = models.CharField(max_length=30, verbose_name='物流名称', help_text='物流名称')

    class Meta:
        verbose_name = '物流商'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.name


class MLSite(models.Model):
    """
    站点
    """

    od_num = models.IntegerField(default=1, verbose_name='排序号', help_text='排序号')
    site_code = models.CharField(max_length=30, verbose_name='站点编号', help_text='站点编号')
    name = models.CharField(max_length=30, verbose_name='站点名称', help_text='站点名称')

    class Meta:
        verbose_name = '站点'
        verbose_name_plural = verbose_name
        ordering = ['od_num']

    def __str__(self):
        return self.name


class ExRate(models.Model):
    """
    汇率
    """

    currency = models.CharField(max_length=10, verbose_name='币种', help_text='币种')
    value = models.FloatField(null=True, blank=True, default=0, verbose_name='汇率', help_text='汇率')
    update_time = models.DateTimeField(null=True, blank=True, verbose_name='更新时间', help_text='更新时间')

    class Meta:
        verbose_name = '汇率'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.currency


class FBMWarehouse(models.Model):
    """
    FBM仓库
    """

    country = models.CharField(max_length=30, null=True, blank=True, verbose_name='国家', help_text='国家')
    w_code = models.CharField(max_length=30, verbose_name='仓库代码', help_text='仓库代码')
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='仓库名称', help_text='仓库名称')
    address = models.CharField(max_length=300, null=True, blank=True, verbose_name='仓库地址', help_text='仓库地址')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='是否启用', help_text='是否启用')

    class Meta:
        verbose_name = 'FBM仓库'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return self.w_code


class MLOrder(models.Model):
    """
    销售订单
    """

    shop = models.ForeignKey(Shop, related_name='shop_order', on_delete=models.CASCADE, verbose_name='所属店铺',
                             help_text='所属店铺')
    order_number = models.CharField(max_length=30, null=True, blank=True, verbose_name='订单编号', help_text='订单编号')
    order_status = models.CharField(max_length=10, null=True, blank=True, verbose_name='订单状态', help_text='订单状态')
    order_time = models.DateTimeField(null=True, blank=True, verbose_name='订单时间', help_text='订单时间')
    order_time_bj = models.DateTimeField(null=True, blank=True, verbose_name='订单北京时间', help_text='订单北京时间')
    qty = models.IntegerField(default=0, verbose_name='数量', help_text='数量')
    currency = models.CharField(max_length=5, null=True, blank=True, verbose_name='币种', help_text='币种')
    ex_rate = models.FloatField(default=0, null=True, blank=True, verbose_name='汇率', help_text='汇率')
    price = models.FloatField(default=0, null=True, blank=True, verbose_name='销售价', help_text='销售价')
    fees = models.FloatField(default=0, null=True, blank=True, verbose_name='佣金', help_text='佣金')
    postage = models.FloatField(default=0, null=True, blank=True, verbose_name='邮费', help_text='邮费')
    receive_fund = models.FloatField(default=0, null=True, blank=True, verbose_name='收入资金', help_text='收入资金')
    profit = models.FloatField(default=0, null=True, blank=True, verbose_name='利润rmb', help_text='利润rmb')
    profit_rate = models.FloatField(default=0, null=True, blank=True, verbose_name='毛利率', help_text='毛利率')
    is_ad = models.BooleanField(default=False, verbose_name='是否广告卖出', help_text='是否广告卖出')
    sku = models.CharField(max_length=30, verbose_name='产品SKU', help_text='产品SKU')
    p_name = models.CharField(max_length=80, verbose_name='产品名称', help_text='产品名称')
    item_id = models.CharField(max_length=30, null=True, blank=True, verbose_name='链接编号', help_text='链接编号')
    image = models.ImageField(null=True, blank=True, upload_to='ml_product', max_length=200, verbose_name='产品图片',
                              help_text='产品图片')
    unit_cost = models.FloatField(null=True, default=0, verbose_name='均摊成本价', help_text='均摊成本价')
    first_ship_cost = models.FloatField(null=True, default=0, verbose_name='均摊头程运费', help_text='均摊头程运费')
    buyer_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='买家姓名', help_text='买家姓名')
    buyer_address = models.CharField(max_length=500, null=True, blank=True, verbose_name='买家街道', help_text='买家街道')
    buyer_city = models.CharField(max_length=50, null=True, blank=True, verbose_name='买家城市', help_text='买家城市')
    buyer_state = models.CharField(max_length=30, null=True, blank=True, verbose_name='买家州', help_text='买家州')
    buyer_postcode = models.CharField(max_length=20, null=True, blank=True, verbose_name='买家邮编', help_text='买家邮编')
    buyer_country = models.CharField(max_length=20, null=True, blank=True, verbose_name='买家国家', help_text='买家国家')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '销售订单'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return self.order_number


class Finance(models.Model):
    """
    财务管理
    """

    shop = models.ForeignKey(Shop, related_name='shop_finance', on_delete=models.CASCADE, verbose_name='所属店铺',
                             help_text='所属店铺')
    currency = models.CharField(max_length=10, null=True, blank=True, verbose_name='币种', help_text='币种')
    income = models.FloatField(null=True, default=0, verbose_name='外汇收入金额', help_text='外汇收入金额')
    wd_date = models.DateField(null=True, blank=True, verbose_name='提现日期', help_text='提现日期')
    rec_date = models.DateField(null=True, blank=True, verbose_name='提现到账日期', help_text='提现到账日期')
    exchange = models.FloatField(null=True, default=0, verbose_name='结汇金额', help_text='结汇金额')
    income_rmb = models.FloatField(null=True, default=0, verbose_name='结汇rmb', help_text='结汇rmb')
    exc_date = models.DateField(null=True, blank=True, verbose_name='结汇日期', help_text='结汇日期')
    f_type = models.CharField(max_length=10, null=True, blank=True, verbose_name='资金类型', help_text='资金类型')
    is_received = models.BooleanField(default=False, verbose_name='外汇是否收到', help_text='外汇是否收到')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '财务管理'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return str(self.shop)