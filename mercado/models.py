from django.db import models


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

    class Meta:
        verbose_name = 'ML产品库'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.sku


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
    url = models.CharField(null=True, blank=True, max_length=300, verbose_name='店铺链接', help_text='店铺链接')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')
    is_active = models.BooleanField(default=True, verbose_name='是否启用', help_text='是否启用')
    total_profit = models.FloatField(null=True, blank=True, verbose_name='累计利润', help_text='累计利润')
    total_weight = models.FloatField(null=True, blank=True, verbose_name='库存总重量kg', help_text='库存总重量kg')
    total_cbm = models.FloatField(null=True, blank=True, verbose_name='库存总体积cbm', help_text='库存总体积cbm')
    stock_value = models.FloatField(null=True, blank=True, verbose_name='库存价值rmb', help_text='库存价值rmb')
    total_qty = models.IntegerField(null=True, blank=True, verbose_name='库存价值rmb', help_text='库存价值rmb')

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
    p_status = models.CharField(max_length=10, choices=PRODUCT_STATUS, default='ON_SALE', verbose_name='产品状态',
                                help_text='产品状态')
    qty = models.IntegerField(default=0, verbose_name='库存数量', help_text='库存数量')
    onway_qty = models.IntegerField(default=0, verbose_name='在途数量', help_text='在途数量')
    day15_sold = models.IntegerField(default=0, verbose_name='15天销量', help_text='15天销量')
    day30_sold = models.IntegerField(default=0, verbose_name='30天销量', help_text='30天销量')
    total_sold = models.IntegerField(default=0, verbose_name='累计销量', help_text='累计销量')
    unit_cost = models.FloatField(null=True, blank=True, verbose_name='均摊成本价', help_text='均摊成本价')
    first_ship_cost = models.FloatField(null=True, blank=True, verbose_name='均摊头程运费', help_text='均摊头程运费')
    length = models.FloatField(null=True, blank=True, verbose_name='长cm', help_text='长cm')
    width = models.FloatField(null=True, blank=True, verbose_name='宽cm', help_text='宽cm')
    heigth = models.FloatField(null=True, blank=True, verbose_name='高cm', help_text='高cm')
    weight = models.FloatField(null=True, blank=True, verbose_name='重量kg', help_text='重量kg')
    total_profit = models.FloatField(null=True, blank=True, verbose_name='累计利润', help_text='累计利润')
    total_weight = models.FloatField(null=True, blank=True, verbose_name='总重量kg', help_text='总重量kg')
    total_cbm = models.FloatField(null=True, blank=True, verbose_name='总体积cbm', help_text='总体积cbm')
    stock_value = models.FloatField(null=True, blank=True, verbose_name='库存价值rmb', help_text='库存价值rmb')
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
