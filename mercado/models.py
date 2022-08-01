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
