from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()


class Listing(models.Model):
    """
    在线产品
    """

    item_id = models.CharField(max_length=20,
                               verbose_name='商品id',
                               help_text='商品id')
    site_id = models.CharField(max_length=10,
                               verbose_name='站点id',
                               help_text='站点id')
    title = models.CharField(max_length=150,
                             verbose_name='商品名称',
                             help_text='商品名称')
    image = models.CharField(null=True,
                             blank=True,
                             max_length=200,
                             verbose_name='主图链接',
                             help_text='主图链接')
    link = models.CharField(null=True,
                            blank=True,
                            max_length=200,
                            verbose_name='商品链接',
                            help_text='商品链接')
    price = models.FloatField(null=True,
                              blank=True,
                              verbose_name='销售定价',
                              help_text='销售定价')
    currency = models.CharField(null=True,
                                blank=True,
                                max_length=5,
                                verbose_name='币种',
                                help_text='币种')
    total_sold = models.IntegerField(default=0,
                                     null=True,
                                     blank=True,
                                     verbose_name='总销量',
                                     help_text='总销量')
    sold_7d = models.IntegerField(default=0,
                                  null=True,
                                  blank=True,
                                  verbose_name='近7天销量',
                                  help_text='近7天销量')
    sold_30d = models.IntegerField(default=0,
                                   null=True,
                                   blank=True,
                                   verbose_name='近30天销量',
                                   help_text='近30天销量')
    reviews = models.IntegerField(default=0,
                                  null=True,
                                  blank=True,
                                  verbose_name='评论数量',
                                  help_text='评论数量')
    rating_average = models.FloatField(null=True,
                                       blank=True,
                                       verbose_name='评分',
                                       help_text='评分')
    start_date = models.DateField(null=True,
                                  verbose_name='上架时间',
                                  help_text='上架时间')
    listing_status = models.CharField(null=True,
                                      blank=True,
                                      max_length=10,
                                      verbose_name='商品状态',
                                      help_text='商品状态')
    health = models.FloatField(null=True,
                               blank=True,
                               verbose_name='健康度',
                               help_text='健康度')
    stock_num = models.IntegerField(default=0,
                                    null=True,
                                    blank=True,
                                    verbose_name='库存数',
                                    help_text='库存数')
    ship_type = models.CharField(null=True,
                                 blank=True,
                                 max_length=20,
                                 verbose_name='物流类型',
                                 help_text='物流类型')
    is_cbt = models.BooleanField(default=True,
                                 verbose_name='是否大陆卖家',
                                 help_text='是否大陆卖家')
    is_free_shipping = models.BooleanField(default=True,
                                           verbose_name='是否免运费',
                                           help_text='是否免运费')
    seller_id = models.CharField(null=True,
                                 blank=True,
                                 max_length=20,
                                 verbose_name='卖家id',
                                 help_text='卖家id')
    seller_name = models.CharField(null=True,
                                   blank=True,
                                   max_length=50,
                                   verbose_name='卖家名称',
                                   help_text='卖家名称')
    brand = models.CharField(null=True,
                             blank=True,
                             max_length=20,
                             verbose_name='品牌名称',
                             help_text='品牌名称')
    collection = models.BooleanField(default=False,
                                     verbose_name='是否收藏',
                                     help_text='是否收藏')
    cost = models.FloatField(null=True,
                             blank=True,
                             verbose_name='商品成本',
                             help_text='商品成本')
    profit = models.FloatField(null=True,
                               blank=True,
                               verbose_name='利润',
                               help_text='利润')
    note = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='备注',
                            help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    update_time = models.DateTimeField(null=True,
                                       verbose_name='数据更新时间',
                                       help_text='数据更新时间')

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

    listing = models.ForeignKey(Listing,
                                related_name='listing_track',
                                on_delete=models.CASCADE,
                                verbose_name='在线产品',
                                help_text='在线产品')
    currency = models.CharField(null=True,
                                blank=True,
                                max_length=5,
                                verbose_name='币种',
                                help_text='币种')
    price = models.FloatField(default=0,
                              null=True,
                              blank=True,
                              verbose_name='销售定价',
                              help_text='销售定价')
    total_sold = models.IntegerField(default=0,
                                     null=True,
                                     blank=True,
                                     verbose_name='总销量',
                                     help_text='总销量')
    today_sold = models.IntegerField(default=0,
                                     null=True,
                                     blank=True,
                                     verbose_name='今天销量',
                                     help_text='今天销量')
    reviews = models.IntegerField(default=0,
                                  null=True,
                                  blank=True,
                                  verbose_name='评论数量',
                                  help_text='评论数量')
    rating_average = models.FloatField(null=True,
                                       blank=True,
                                       verbose_name='评分',
                                       help_text='评分')
    health = models.FloatField(null=True,
                               blank=True,
                               verbose_name='健康度',
                               help_text='健康度')
    stock_num = models.IntegerField(default=0,
                                    null=True,
                                    blank=True,
                                    verbose_name='库存数',
                                    help_text='库存数')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')

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

    seller_id = models.CharField(max_length=10,
                                 verbose_name='卖家id',
                                 help_text='卖家id')
    site_id = models.CharField(max_length=10,
                               verbose_name='站点id',
                               help_text='站点id')
    nickname = models.CharField(max_length=50,
                                verbose_name='卖家名称',
                                help_text='卖家名称')
    level_id = models.CharField(max_length=30,
                                verbose_name='信誉水平',
                                help_text='信誉水平')
    total = models.IntegerField(default=0,
                                null=True,
                                blank=True,
                                verbose_name='总订单',
                                help_text='总订单')
    canceled = models.IntegerField(default=0,
                                   null=True,
                                   blank=True,
                                   verbose_name='取消订单',
                                   help_text='取消订单')
    negative = models.FloatField(null=True,
                                 blank=True,
                                 verbose_name='差评率',
                                 help_text='差评率')
    neutral = models.FloatField(null=True,
                                blank=True,
                                verbose_name='中评率',
                                help_text='中评率')
    positive = models.FloatField(null=True,
                                 blank=True,
                                 verbose_name='好评率',
                                 help_text='好评率')
    registration_date = models.DateField(null=True,
                                         verbose_name='注册日期',
                                         help_text='注册日期')
    link = models.CharField(null=True,
                            blank=True,
                            max_length=200,
                            verbose_name='店铺链接',
                            help_text='店铺链接')
    sold_60d = models.IntegerField(default=0,
                                   null=True,
                                   blank=True,
                                   verbose_name='60天销量',
                                   help_text='60天销量')
    total_items = models.IntegerField(default=0,
                                      null=True,
                                      blank=True,
                                      verbose_name='listing数量',
                                      help_text='listing数量')
    collection = models.BooleanField(default=False,
                                     verbose_name='是否收藏',
                                     help_text='是否收藏')
    update_time = models.DateTimeField(null=True,
                                       verbose_name='更新时间',
                                       help_text='更新时间')
    note = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='备注',
                            help_text='备注')

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

    seller = models.ForeignKey(Seller,
                               related_name='seller_track',
                               on_delete=models.CASCADE,
                               verbose_name='卖家',
                               help_text='卖家')
    total = models.IntegerField(default=0,
                                null=True,
                                blank=True,
                                verbose_name='总订单',
                                help_text='总订单')
    today_sold = models.IntegerField(default=0,
                                     null=True,
                                     blank=True,
                                     verbose_name='今天订单',
                                     help_text='今天订单')
    negative = models.FloatField(null=True,
                                 blank=True,
                                 verbose_name='差评率',
                                 help_text='差评率')
    neutral = models.FloatField(null=True,
                                blank=True,
                                verbose_name='中评率',
                                help_text='中评率')
    positive = models.FloatField(null=True,
                                 blank=True,
                                 verbose_name='好评率',
                                 help_text='好评率')
    total_items = models.IntegerField(default=0,
                                      null=True,
                                      blank=True,
                                      verbose_name='listing数量',
                                      help_text='listing数量')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')

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

    categ_id = models.CharField(max_length=10,
                                verbose_name='类目id',
                                help_text='类目id')
    father_id = models.CharField(null=True,
                                 max_length=10,
                                 verbose_name='父类目id',
                                 help_text='父类目id')
    site_id = models.CharField(max_length=10,
                               verbose_name='站点id',
                               help_text='站点id')
    name = models.CharField(null=True,
                            max_length=100,
                            verbose_name='类目名称',
                            help_text='类目名称')
    t_name = models.CharField(null=True,
                              blank=True,
                              max_length=100,
                              verbose_name='翻译类目名称',
                              help_text='翻译类目名称')
    path_from_root = models.CharField(max_length=200,
                                      verbose_name='类目导航',
                                      help_text='类目导航')
    total_items = models.IntegerField(default=0,
                                      null=True,
                                      blank=True,
                                      verbose_name='类目产品数量',
                                      help_text='类目产品数量')
    has_children = models.BooleanField(default=True,
                                       verbose_name='是否有子类目',
                                       help_text='是否有子类目')
    collection = models.BooleanField(default=False,
                                     verbose_name='是否收藏',
                                     help_text='是否收藏')
    update_time = models.DateTimeField(null=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')

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

    categ_id = models.CharField(max_length=10,
                                verbose_name='类目id',
                                help_text='类目id')
    keyword = models.CharField(null=True,
                               max_length=100,
                               verbose_name='关键词',
                               help_text='关键词')
    t_keyword = models.CharField(null=True,
                                 blank=True,
                                 max_length=100,
                                 verbose_name='关键词翻译',
                                 help_text='关键词翻译')
    url = models.CharField(null=True,
                           blank=True,
                           max_length=200,
                           verbose_name='url',
                           help_text='url')
    rank = models.IntegerField(default=0,
                               null=True,
                               blank=True,
                               verbose_name='排名',
                               help_text='排名')
    status = models.CharField(null=True,
                              blank=True,
                              max_length=5,
                              verbose_name='状态',
                              help_text='状态')
    rank_changed = models.IntegerField(default=0,
                                       null=True,
                                       blank=True,
                                       verbose_name='排名变化',
                                       help_text='排名变化')
    update_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')

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

    access_token = models.CharField(max_length=50,
                                    verbose_name='api-token',
                                    help_text='api-token')

    class Meta:
        verbose_name = 'api设置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.access_token


class TransApiSetting(models.Model):
    """
    百度翻译api设置
    """

    appid = models.CharField(max_length=50,
                             verbose_name='appid',
                             help_text='appid')
    secretKey = models.CharField(max_length=50,
                                 verbose_name='secretKey',
                                 help_text='secretKey')

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

    sku = models.CharField(max_length=30,
                           verbose_name='产品SKU',
                           help_text='产品SKU')
    p_name = models.CharField(max_length=80,
                              verbose_name='产品名称',
                              help_text='产品名称')
    label_code = models.CharField(max_length=30,
                                  null=True,
                                  blank=True,
                                  verbose_name='FBM条码',
                                  help_text='FBM条码')
    upc = models.CharField(max_length=30,
                           null=True,
                           blank=True,
                           verbose_name='UPC',
                           help_text='UPC')
    item_id = models.CharField(max_length=30,
                               null=True,
                               blank=True,
                               verbose_name='链接编号',
                               help_text='链接编号')
    image = models.ImageField(null=True,
                              blank=True,
                              upload_to='ml_product',
                              max_length=200,
                              verbose_name='产品图片',
                              help_text='产品图片')
    p_status = models.CharField(max_length=10,
                                choices=PRODUCT_STATUS,
                                default='ON_SALE',
                                verbose_name='产品状态',
                                help_text='产品状态')
    platform = models.CharField(max_length=20,
                                null=True,
                                blank=True,
                                verbose_name='平台',
                                help_text='平台')
    custom_code = models.CharField(null=True,
                                   blank=True,
                                   max_length=20,
                                   verbose_name='海关编码',
                                   help_text='海关编码')
    cn_name = models.CharField(null=True,
                               blank=True,
                               max_length=30,
                               verbose_name='中文品名',
                               help_text='中文品名')
    en_name = models.CharField(null=True,
                               blank=True,
                               max_length=30,
                               verbose_name='英文品名',
                               help_text='英文品名')
    brand = models.CharField(null=True,
                             blank=True,
                             max_length=20,
                             verbose_name='品牌',
                             help_text='品牌')
    declared_value = models.FloatField(null=True,
                                       blank=True,
                                       max_length=30,
                                       verbose_name='申报价值USD',
                                       help_text='申报价值USD')
    cn_material = models.CharField(null=True,
                                   blank=True,
                                   max_length=30,
                                   verbose_name='中文材质',
                                   help_text='中文材质')
    en_material = models.CharField(null=True,
                                   blank=True,
                                   max_length=30,
                                   verbose_name='英文材质',
                                   help_text='英文材质')
    use = models.CharField(null=True,
                           blank=True,
                           max_length=50,
                           verbose_name='用途',
                           help_text='用途')
    is_elec = models.BooleanField(default=False,
                                  null=True,
                                  verbose_name='是否带电',
                                  help_text='是否带电')
    is_magnet = models.BooleanField(default=False,
                                    null=True,
                                    verbose_name='是否带磁',
                                    help_text='是否带磁')
    is_water = models.BooleanField(default=False,
                                   null=True,
                                   verbose_name='是否带液体',
                                   help_text='是否带液体')
    site = models.CharField(null=True,
                            blank=True,
                            max_length=30,
                            verbose_name='站点',
                            help_text='站点')
    shop = models.CharField(null=True,
                            blank=True,
                            max_length=50,
                            verbose_name='上架店铺',
                            help_text='上架店铺')

    unit_cost = models.FloatField(null=True,
                                  blank=True,
                                  verbose_name='成本价',
                                  help_text='成本价')
    first_ship_cost = models.FloatField(null=True,
                                        blank=True,
                                        verbose_name='预估头程运费',
                                        help_text='预估头程运费')
    length = models.FloatField(null=True,
                               blank=True,
                               verbose_name='长cm',
                               help_text='长cm')
    width = models.FloatField(null=True,
                              blank=True,
                              verbose_name='宽cm',
                              help_text='宽cm')
    heigth = models.FloatField(null=True,
                               blank=True,
                               verbose_name='高cm',
                               help_text='高cm')
    weight = models.FloatField(null=True,
                               blank=True,
                               verbose_name='重量kg',
                               help_text='重量kg')
    buy_url = models.CharField(null=True,
                               blank=True,
                               max_length=500,
                               verbose_name='产品采购链接',
                               help_text='产品采购链接')
    sale_url = models.CharField(null=True,
                                blank=True,
                                max_length=500,
                                verbose_name='销售链接',
                                help_text='销售链接')
    refer_url = models.CharField(null=True,
                                 blank=True,
                                 max_length=500,
                                 verbose_name='参考链接',
                                 help_text='参考链接')
    note = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='备注',
                            help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    is_checked = models.BooleanField(default=False,
                                     null=True,
                                     verbose_name='是否核对',
                                     help_text='是否核对')
    label_title = models.CharField(null=True,
                                   blank=True,
                                   max_length=100,
                                   verbose_name='链接标题',
                                   help_text='链接标题')
    label_option = models.CharField(null=True,
                                    blank=True,
                                    max_length=50,
                                    verbose_name='链接选项',
                                    help_text='链接选项')
    packing_id = models.IntegerField(null=True,
                                     blank=True,
                                     verbose_name='包材id',
                                     help_text='包材id')
    buy_url2 = models.CharField(null=True,
                                blank=True,
                                max_length=500,
                                verbose_name='产品采购链接2',
                                help_text='产品采购链接2')
    buy_url3 = models.CharField(null=True,
                                blank=True,
                                max_length=500,
                                verbose_name='产品采购链接3',
                                help_text='产品采购链接3')
    buy_url4 = models.CharField(null=True,
                                blank=True,
                                max_length=500,
                                verbose_name='产品采购链接4',
                                help_text='产品采购链接4')
    buy_url5 = models.CharField(null=True,
                                blank=True,
                                max_length=500,
                                verbose_name='产品采购链接5',
                                help_text='产品采购链接5')
    user_id = models.IntegerField(default=0,
                                  null=True,
                                  blank=True,
                                  verbose_name='创建人id',
                                  help_text='创建人id')

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

    name = models.CharField(max_length=80,
                            verbose_name='包材名称',
                            help_text='包材名称')
    size = models.CharField(max_length=80, verbose_name='尺寸', help_text='尺寸')
    weight = models.FloatField(default=0,
                               null=True,
                               blank=True,
                               verbose_name='重量g',
                               help_text='重量g')
    note = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='备注',
                            help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')

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

    warehouse_type = models.CharField(max_length=30,
                                      verbose_name='仓库类型',
                                      help_text='仓库类型')
    platform = models.CharField(max_length=20,
                                null=True,
                                blank=True,
                                verbose_name='平台',
                                help_text='平台')
    name = models.CharField(max_length=30,
                            verbose_name='店铺代号',
                            help_text='店铺代号')
    shop_type = models.CharField(max_length=30,
                                 null=True,
                                 blank=True,
                                 verbose_name='店铺类型',
                                 help_text='店铺类型')
    seller_id = models.CharField(max_length=30,
                                 null=True,
                                 blank=True,
                                 verbose_name='店铺ID',
                                 help_text='店铺ID')
    nickname = models.CharField(max_length=50,
                                null=True,
                                blank=True,
                                verbose_name='店铺名称',
                                help_text='店铺名称')
    site = models.CharField(max_length=20,
                            null=True,
                            blank=True,
                            verbose_name='站点',
                            help_text='站点')
    currency = models.CharField(max_length=10,
                                null=True,
                                blank=True,
                                verbose_name='币种',
                                help_text='币种')
    exc_currency = models.CharField(max_length=5,
                                    null=True,
                                    blank=True,
                                    verbose_name='结算币种',
                                    help_text='结算币种')
    url = models.CharField(null=True,
                           blank=True,
                           max_length=300,
                           verbose_name='店铺链接',
                           help_text='店铺链接')
    note = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='备注',
                            help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    is_active = models.BooleanField(default=True,
                                    verbose_name='是否启用',
                                    help_text='是否启用')
    total_profit = models.FloatField(null=True,
                                     blank=True,
                                     verbose_name='累计利润',
                                     help_text='累计利润')
    total_weight = models.FloatField(null=True,
                                     blank=True,
                                     verbose_name='库存总重量kg',
                                     help_text='库存总重量kg')
    total_cbm = models.FloatField(null=True,
                                  blank=True,
                                  verbose_name='库存总体积cbm',
                                  help_text='库存总体积cbm')
    stock_value = models.FloatField(null=True,
                                    blank=True,
                                    verbose_name='库存价值rmb',
                                    help_text='库存价值rmb')
    quota = models.FloatField(null=True,
                              blank=True,
                              verbose_name='店铺额度',
                              help_text='店铺额度')
    total_qty = models.IntegerField(null=True,
                                    blank=True,
                                    verbose_name='库存价值rmb',
                                    help_text='库存价值rmb')
    user = models.ForeignKey(User,
                             related_name='user_shop',
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True,
                             verbose_name='user',
                             help_text='user')
    name_color = models.CharField(max_length=20,
                                  null=True,
                                  blank=True,
                                  verbose_name='店铺名称颜色',
                                  help_text='店铺名称颜色')

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

    shop = models.ForeignKey(Shop,
                             related_name='shop_shopstock',
                             on_delete=models.CASCADE,
                             verbose_name='上架店铺',
                             help_text='上架店铺')
    sku = models.CharField(max_length=30,
                           verbose_name='产品SKU',
                           help_text='产品SKU')
    p_name = models.CharField(max_length=80,
                              verbose_name='产品名称',
                              help_text='产品名称')
    label_code = models.CharField(max_length=30,
                                  null=True,
                                  blank=True,
                                  verbose_name='FBM条码',
                                  help_text='FBM条码')
    upc = models.CharField(max_length=30,
                           null=True,
                           blank=True,
                           verbose_name='UPC',
                           help_text='UPC')
    item_id = models.CharField(max_length=30,
                               null=True,
                               blank=True,
                               verbose_name='链接编号',
                               help_text='链接编号')
    image = models.ImageField(null=True,
                              blank=True,
                              upload_to='ml_product',
                              max_length=200,
                              verbose_name='产品图片',
                              help_text='产品图片')
    p_status = models.CharField(max_length=10,
                                choices=PRODUCT_STATUS,
                                default='NORMAL',
                                verbose_name='产品状态',
                                help_text='产品状态')
    qty = models.IntegerField(default=0, verbose_name='库存数量', help_text='库存数量')
    onway_qty = models.IntegerField(default=0,
                                    verbose_name='在途数量',
                                    help_text='在途数量')
    trans_qty = models.IntegerField(default=0,
                                    verbose_name='中转仓数量',
                                    help_text='中转仓数量')
    day7_sold = models.IntegerField(default=0,
                                    verbose_name='7天销量',
                                    help_text='7天销量')
    day15_sold = models.IntegerField(default=0,
                                     verbose_name='15天销量',
                                     help_text='15天销量')
    day30_sold = models.IntegerField(default=0,
                                     verbose_name='30天销量',
                                     help_text='30天销量')
    total_sold = models.IntegerField(default=0,
                                     verbose_name='累计销量',
                                     help_text='累计销量')
    unit_cost = models.FloatField(null=True,
                                  default=0,
                                  verbose_name='均摊成本价',
                                  help_text='均摊成本价')
    first_ship_cost = models.FloatField(null=True,
                                        default=0,
                                        verbose_name='均摊头程运费',
                                        help_text='均摊头程运费')
    length = models.FloatField(null=True,
                               blank=True,
                               verbose_name='长cm',
                               help_text='长cm')
    width = models.FloatField(null=True,
                              blank=True,
                              verbose_name='宽cm',
                              help_text='宽cm')
    heigth = models.FloatField(null=True,
                               blank=True,
                               verbose_name='高cm',
                               help_text='高cm')
    weight = models.FloatField(null=True,
                               blank=True,
                               verbose_name='重量kg',
                               help_text='重量kg')
    total_profit = models.FloatField(null=True,
                                     blank=True,
                                     verbose_name='累计利润',
                                     help_text='累计利润')
    total_weight = models.FloatField(null=True,
                                     blank=True,
                                     verbose_name='总重量kg',
                                     help_text='总重量kg')
    total_cbm = models.FloatField(null=True,
                                  blank=True,
                                  verbose_name='总体积cbm',
                                  help_text='总体积cbm')
    stock_value = models.FloatField(null=True,
                                    blank=True,
                                    verbose_name='库存价值rmb',
                                    help_text='库存价值rmb')
    refund_rate = models.FloatField(null=True,
                                    blank=True,
                                    verbose_name='退款率',
                                    help_text='退款率')
    avg_profit = models.FloatField(null=True,
                                   blank=True,
                                   verbose_name='平均毛利润',
                                   help_text='平均毛利润')
    avg_profit_rate = models.FloatField(null=True,
                                        blank=True,
                                        verbose_name='平均毛利率',
                                        help_text='平均毛利率')
    sale_url = models.CharField(null=True,
                                blank=True,
                                max_length=500,
                                verbose_name='销售链接',
                                help_text='销售链接')
    note = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='备注',
                            help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    is_active = models.BooleanField(default=True,
                                    verbose_name='是否启用',
                                    help_text='是否启用')
    is_collect = models.BooleanField(default=True,
                                     verbose_name='是否收藏',
                                     help_text='是否收藏')

    class Meta:
        verbose_name = '店铺库存'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.sku


class StockLog(models.Model):
    shop_stock = models.ForeignKey(ShopStock,
                                   related_name='shop_stock_log',
                                   on_delete=models.CASCADE,
                                   verbose_name='所属库存',
                                   help_text='所属库存')
    current_stock = models.IntegerField(default=0,
                                        verbose_name='当前库存',
                                        help_text='当前库存')
    qty = models.IntegerField(default=0, verbose_name='变动数量', help_text='变动数量')
    in_out = models.CharField(max_length=5,
                              verbose_name='库存出入',
                              help_text='库存出入')
    action = models.CharField(max_length=10,
                              verbose_name='变动来源',
                              help_text='变动来源')
    desc = models.CharField(max_length=100, verbose_name='描述', help_text='描述')
    user_id = models.IntegerField(default=0,
                                  null=True,
                                  blank=True,
                                  verbose_name='操作人id',
                                  help_text='操作人id')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')

    class Meta:
        verbose_name = '库存日志'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.action


class TransStock(models.Model):
    """
    中转仓库存
    """
    shop = models.ForeignKey(Shop,
                             related_name='shop_trans_stock',
                             on_delete=models.CASCADE,
                             verbose_name='所属中转仓',
                             help_text='所属中转仓')
    listing_shop = models.CharField(max_length=60,
                                    null=True,
                                    blank=True,
                                    verbose_name='上架店铺',
                                    help_text='上架店铺')
    sku = models.CharField(max_length=30,
                           verbose_name='产品SKU',
                           help_text='产品SKU')
    p_name = models.CharField(max_length=80,
                              verbose_name='产品名称',
                              help_text='产品名称')
    label_code = models.CharField(max_length=30,
                                  null=True,
                                  blank=True,
                                  verbose_name='FBM条码',
                                  help_text='FBM条码')
    upc = models.CharField(max_length=30,
                           null=True,
                           blank=True,
                           verbose_name='UPC',
                           help_text='UPC')
    item_id = models.CharField(max_length=30,
                               null=True,
                               blank=True,
                               verbose_name='链接编号',
                               help_text='链接编号')
    image = models.ImageField(null=True,
                              blank=True,
                              upload_to='ml_product',
                              max_length=200,
                              verbose_name='产品图片',
                              help_text='产品图片')
    qty = models.IntegerField(default=0, verbose_name='库存数量', help_text='库存数量')
    unit_cost = models.FloatField(null=True,
                                  default=0,
                                  verbose_name='均摊成本价',
                                  help_text='均摊成本价')
    first_ship_cost = models.FloatField(null=True,
                                        default=0,
                                        verbose_name='均摊头程运费',
                                        help_text='均摊头程运费')
    s_number = models.CharField(max_length=30,
                                null=True,
                                blank=True,
                                verbose_name='运单编号',
                                help_text='运单编号')
    batch = models.CharField(max_length=30,
                             null=True,
                             blank=True,
                             verbose_name='批次号',
                             help_text='批次号')
    box_number = models.CharField(max_length=30,
                                  verbose_name='箱号',
                                  help_text='箱号')
    carrier_box_number = models.CharField(max_length=30,
                                          null=True,
                                          blank=True,
                                          verbose_name='物流商箱唛号',
                                          help_text='物流商箱唛号')
    box_length = models.FloatField(null=True,
                                   blank=True,
                                   verbose_name='长cm',
                                   help_text='长cm')
    box_width = models.FloatField(null=True,
                                  blank=True,
                                  verbose_name='宽cm',
                                  help_text='宽cm')
    box_heigth = models.FloatField(null=True,
                                   blank=True,
                                   verbose_name='高cm',
                                   help_text='高cm')
    box_weight = models.FloatField(null=True,
                                   blank=True,
                                   verbose_name='重量kg',
                                   help_text='重量kg')
    box_cbm = models.FloatField(null=True,
                                blank=True,
                                verbose_name='体积cbm',
                                help_text='体积cbm')
    note = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='备注',
                            help_text='备注')
    arrived_date = models.DateField(null=True,
                                    blank=True,
                                    verbose_name='到仓日期',
                                    help_text='到仓日期')
    is_out = models.BooleanField(default=False,
                                 verbose_name='是否已出仓',
                                 help_text='是否已出仓')
    out_time = models.DateTimeField(null=True,
                                    blank=True,
                                    verbose_name='出仓时间',
                                    help_text='出仓时间')
    user_id = models.IntegerField(default=0,
                                  null=True,
                                  blank=True,
                                  verbose_name='创建人id',
                                  help_text='创建人id')

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

    s_number = models.CharField(max_length=30,
                                null=True,
                                blank=True,
                                verbose_name='运单编号',
                                help_text='运单编号')
    platform = models.CharField(max_length=20,
                                null=True,
                                blank=True,
                                verbose_name='平台',
                                help_text='平台')
    batch = models.CharField(max_length=30,
                             null=True,
                             blank=True,
                             verbose_name='批次号',
                             help_text='批次号')
    s_status = models.CharField(max_length=10,
                                choices=SHIP_STATUS,
                                default='PREPARING',
                                verbose_name='产品状态',
                                help_text='产品状态')
    shop = models.CharField(max_length=30,
                            null=True,
                            blank=True,
                            verbose_name='目标店铺',
                            help_text='目标店铺')
    target = models.CharField(max_length=30,
                              null=True,
                              blank=True,
                              verbose_name='目标入仓FBM/中转仓',
                              help_text='目标入仓FBM/中转仓')
    fbm_warehouse = models.CharField(max_length=30,
                                     null=True,
                                     blank=True,
                                     verbose_name='fbm仓库',
                                     help_text='fbm仓库')
    envio_number = models.CharField(max_length=30,
                                    null=True,
                                    blank=True,
                                    verbose_name='Envio号',
                                    help_text='Envio号')
    send_from = models.CharField(max_length=30,
                                 null=True,
                                 blank=True,
                                 verbose_name='从哪发',
                                 help_text='从哪发')
    ship_type = models.CharField(max_length=10,
                                 null=True,
                                 blank=True,
                                 verbose_name='运单类型',
                                 help_text='运单类型')
    shipping_fee = models.FloatField(null=True,
                                     default=0,
                                     verbose_name='运费',
                                     help_text='运费')
    logi_fee_clear = models.BooleanField(default=False,
                                         verbose_name='物流费是否结算',
                                         help_text='物流费是否结算')
    extra_fee = models.FloatField(null=True,
                                  default=0,
                                  verbose_name='额外费用',
                                  help_text='额外费用')
    products_cost = models.FloatField(null=True,
                                      default=0,
                                      verbose_name='货品成本',
                                      help_text='货品成本')
    carrier = models.CharField(max_length=30,
                               null=True,
                               blank=True,
                               verbose_name='承运商',
                               help_text='承运商')
    carrier_order_status = models.CharField(max_length=10,
                                            null=True,
                                            blank=True,
                                            verbose_name='物流交运订单状态',
                                            help_text='物流交运订单状态')
    carrier_order_time = models.DateTimeField(null=True,
                                              blank=True,
                                              verbose_name='物流交运时间',
                                              help_text='物流交运时间')
    carrier_rec_check = models.CharField(max_length=10,
                                         null=True,
                                         blank=True,
                                         verbose_name='物流收货核查',
                                         help_text='物流收货核查')
    carrier_ckweight = models.FloatField(null=True,
                                         blank=True,
                                         verbose_name='收货重量',
                                         help_text='收货重量')
    carrier_ckcbm = models.FloatField(null=True,
                                      blank=True,
                                      verbose_name='收货体积',
                                      help_text='收货体积')
    carrier_ckvolume = models.FloatField(null=True,
                                         blank=True,
                                         verbose_name='计费重量',
                                         help_text='计费重量')
    carrier_GoodsNum = models.IntegerField(default=0,
                                           verbose_name='收货箱数',
                                           help_text='收货箱数')
    end_date = models.DateField(null=True,
                                blank=True,
                                verbose_name='物流截单日期',
                                help_text='物流截单日期')
    ship_date = models.DateField(null=True,
                                 blank=True,
                                 verbose_name='航班日期',
                                 help_text='航班日期')
    book_date = models.DateField(null=True,
                                 blank=True,
                                 verbose_name='FBM预约日期',
                                 help_text='FBM预约日期')
    total_box = models.IntegerField(default=0,
                                    verbose_name='总箱数',
                                    help_text='总箱数')
    total_qty = models.IntegerField(default=0,
                                    verbose_name='总数量',
                                    help_text='总数量')
    weight = models.FloatField(null=True,
                               blank=True,
                               verbose_name='总重量kg',
                               help_text='总重量kg')
    cbm = models.FloatField(null=True,
                            blank=True,
                            verbose_name='总体积cbm',
                            help_text='总体积cbm')
    tag_name = models.CharField(max_length=100,
                                null=True,
                                blank=True,
                                verbose_name='标签名称',
                                help_text='标签名称')
    tag_color = models.CharField(max_length=20,
                                 null=True,
                                 blank=True,
                                 verbose_name='标签颜色',
                                 help_text='标签颜色')
    user_id = models.IntegerField(default=0,
                                  null=True,
                                  blank=True,
                                  verbose_name='创建人id',
                                  help_text='创建人id')
    note = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='备注',
                            help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    sent_time = models.DateTimeField(null=True,
                                     blank=True,
                                     verbose_name='发货时间',
                                     help_text='发货时间')

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
    ship = models.ForeignKey(Ship,
                             related_name='ship_shipDetail',
                             on_delete=models.CASCADE,
                             verbose_name='所属运单',
                             help_text='所属运单')
    target_FBM = models.CharField(max_length=30,
                                  null=True,
                                  blank=True,
                                  verbose_name='目标FBM仓库',
                                  help_text='目标FBM仓库')
    box_number = models.CharField(max_length=30,
                                  verbose_name='箱号',
                                  help_text='箱号')
    s_type = models.CharField(max_length=10,
                              verbose_name='发货类型',
                              help_text='发货类型')
    sku = models.CharField(max_length=30,
                           verbose_name='产品SKU',
                           help_text='产品SKU')
    p_name = models.CharField(max_length=80,
                              verbose_name='产品名称',
                              help_text='产品名称')
    label_code = models.CharField(max_length=30,
                                  null=True,
                                  blank=True,
                                  verbose_name='FBM条码',
                                  help_text='FBM条码')
    upc = models.CharField(max_length=30,
                           null=True,
                           blank=True,
                           verbose_name='UPC',
                           help_text='UPC')
    item_id = models.CharField(max_length=30,
                               null=True,
                               blank=True,
                               verbose_name='链接编号',
                               help_text='链接编号')
    image = models.ImageField(null=True,
                              blank=True,
                              upload_to='ml_product',
                              max_length=200,
                              verbose_name='产品图片',
                              help_text='产品图片')
    custom_code = models.CharField(null=True,
                                   blank=True,
                                   max_length=20,
                                   verbose_name='海关编码',
                                   help_text='海关编码')
    cn_name = models.CharField(null=True,
                               blank=True,
                               max_length=30,
                               verbose_name='中文品名',
                               help_text='中文品名')
    en_name = models.CharField(null=True,
                               blank=True,
                               max_length=30,
                               verbose_name='英文品名',
                               help_text='英文品名')
    brand = models.CharField(null=True,
                             blank=True,
                             max_length=20,
                             verbose_name='品牌',
                             help_text='品牌')
    declared_value = models.FloatField(null=True,
                                       blank=True,
                                       max_length=30,
                                       verbose_name='申报价值USD',
                                       help_text='申报价值USD')
    cn_material = models.CharField(null=True,
                                   blank=True,
                                   max_length=30,
                                   verbose_name='中文材质',
                                   help_text='中文材质')
    en_material = models.CharField(null=True,
                                   blank=True,
                                   max_length=30,
                                   verbose_name='英文材质',
                                   help_text='英文材质')
    use = models.CharField(null=True,
                           blank=True,
                           max_length=50,
                           verbose_name='用途',
                           help_text='用途')
    is_elec = models.BooleanField(default=False,
                                  null=True,
                                  verbose_name='是否带电',
                                  help_text='是否带电')
    is_magnet = models.BooleanField(default=False,
                                    null=True,
                                    verbose_name='是否带磁',
                                    help_text='是否带磁')
    is_water = models.BooleanField(default=False,
                                   null=True,
                                   verbose_name='是否带液体',
                                   help_text='是否带液体')
    unit_cost = models.FloatField(null=True,
                                  default=0,
                                  verbose_name='成本价',
                                  help_text='成本价')
    avg_ship_fee = models.FloatField(null=True,
                                     default=0,
                                     verbose_name='单个分摊运费',
                                     help_text='单个分摊运费')
    qty = models.IntegerField(default=0, verbose_name='数量', help_text='数量')
    length = models.FloatField(null=True,
                               blank=True,
                               verbose_name='长cm',
                               help_text='长cm')
    width = models.FloatField(null=True,
                              blank=True,
                              verbose_name='宽cm',
                              help_text='宽cm')
    heigth = models.FloatField(null=True,
                               blank=True,
                               verbose_name='高cm',
                               help_text='高cm')
    weight = models.FloatField(null=True,
                               blank=True,
                               verbose_name='重量kg',
                               help_text='重量kg')
    note = models.CharField(max_length=300,
                            null=True,
                            blank=True,
                            verbose_name='短备注',
                            help_text='短备注')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    packing_name = models.CharField(null=True,
                                    blank=True,
                                    max_length=80,
                                    verbose_name='包材名称',
                                    help_text='包材名称')
    packing_size = models.CharField(null=True,
                                    blank=True,
                                    max_length=80,
                                    verbose_name='包材尺寸',
                                    help_text='包材尺寸')
    plan_qty = models.IntegerField(default=0,
                                   verbose_name='后台计划数量',
                                   help_text='后台计划数量')

    class Meta:
        verbose_name = '运单详情'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.sku


class ShipItemRemove(models.Model):
    """
    遗弃清单
    """
    ship = models.ForeignKey(Ship,
                             related_name='ship_itemRemove',
                             on_delete=models.CASCADE,
                             verbose_name='所属运单',
                             help_text='所属运单')
    item_type = models.CharField(max_length=10,
                                 verbose_name='遗弃类型',
                                 help_text='遗弃类型')
    sku = models.CharField(max_length=30,
                           verbose_name='产品SKU',
                           help_text='产品SKU')
    belong_shop = models.CharField(null=True,
                                   blank=True,
                                   max_length=30,
                                   verbose_name='产品所属店铺',
                                   help_text='产品所属店铺')
    p_name = models.CharField(max_length=80,
                              verbose_name='产品名称',
                              help_text='产品名称')
    item_id = models.CharField(max_length=30,
                               null=True,
                               blank=True,
                               verbose_name='链接编号',
                               help_text='链接编号')
    image = models.ImageField(null=True,
                              blank=True,
                              upload_to='ml_product',
                              max_length=200,
                              verbose_name='产品图片',
                              help_text='产品图片')
    plan_qty = models.IntegerField(default=0,
                                   null=True,
                                   blank=True,
                                   verbose_name='计划数量',
                                   help_text='计划数量')
    send_qty = models.IntegerField(default=0,
                                   null=True,
                                   blank=True,
                                   verbose_name='发货数量',
                                   help_text='发货数量')
    note = models.CharField(max_length=300,
                            null=True,
                            blank=True,
                            verbose_name='移除原因',
                            help_text='移除原因')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    handle = models.IntegerField(default=0,
                                 null=True,
                                 blank=True,
                                 verbose_name='处理结果',
                                 help_text='处理结果')
    handle_time = models.DateTimeField(null=True,
                                       blank=True,
                                       verbose_name='处理时间',
                                       help_text='处理时间')

    class Meta:
        verbose_name = '遗弃清单'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return self.sku


class ShipBox(models.Model):
    """
    包装箱
    """
    ship = models.ForeignKey(Ship,
                             related_name='ship_shipBox',
                             on_delete=models.CASCADE,
                             verbose_name='所属运单',
                             help_text='所属运单')
    box_number = models.CharField(max_length=30,
                                  verbose_name='箱号',
                                  help_text='箱号')
    carrier_box_number = models.CharField(max_length=30,
                                          null=True,
                                          blank=True,
                                          verbose_name='物流商箱唛号',
                                          help_text='物流商箱唛号')
    item_qty = models.IntegerField(default=0,
                                   verbose_name='箱内产品数量',
                                   help_text='箱内产品数量')
    length = models.FloatField(null=True,
                               blank=True,
                               verbose_name='长cm',
                               help_text='长cm')
    width = models.FloatField(null=True,
                              blank=True,
                              verbose_name='宽cm',
                              help_text='宽cm')
    heigth = models.FloatField(null=True,
                               blank=True,
                               verbose_name='高cm',
                               help_text='高cm')
    weight = models.FloatField(null=True,
                               blank=True,
                               verbose_name='重量kg',
                               help_text='重量kg')
    cbm = models.FloatField(null=True,
                            blank=True,
                            verbose_name='体积cbm',
                            help_text='体积cbm')
    size_weight = models.FloatField(null=True,
                                    blank=True,
                                    verbose_name='体积重kg',
                                    help_text='体积重kg')
    note = models.CharField(max_length=300,
                            null=True,
                            blank=True,
                            verbose_name='短备注',
                            help_text='短备注')

    class Meta:
        verbose_name = '包装箱'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.box_number


class ShipAttachment(models.Model):
    """
    运单附件
    """
    ship = models.ForeignKey(Ship,
                             related_name='ship_attachment',
                             on_delete=models.CASCADE,
                             verbose_name='所属运单',
                             help_text='所属运单')
    a_type = models.CharField(max_length=10,
                              verbose_name='附件类型',
                              help_text='附件类型')
    name = models.CharField(max_length=100,
                            null=True,
                            blank=True,
                            verbose_name='附件名称',
                            help_text='附件名称')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')

    class Meta:
        verbose_name = '运单附件'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.name


class CarrierTrack(models.Model):
    """
    运单物流跟踪
    """

    carrier_name = models.CharField(null=True,
                                    blank=True,
                                    max_length=30,
                                    verbose_name='物流商名称',
                                    help_text='物流商名称')
    carrier_number = models.CharField(null=True,
                                      blank=True,
                                      max_length=30,
                                      verbose_name='物流商单号',
                                      help_text='物流商单号')
    context = models.CharField(null=True,
                               blank=True,
                               max_length=100,
                               verbose_name='节点描述',
                               help_text='节点描述')
    location = models.CharField(null=True,
                                blank=True,
                                max_length=30,
                                verbose_name='位置',
                                help_text='位置')
    status = models.CharField(null=True,
                              blank=True,
                              max_length=30,
                              verbose_name='状态',
                              help_text='状态')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    time = models.DateTimeField(null=True,
                                blank=True,
                                verbose_name='时间',
                                help_text='时间')
    optime = models.DateTimeField(null=True,
                                  blank=True,
                                  verbose_name='操作时间',
                                  help_text='操作时间')

    class Meta:
        verbose_name = '物流跟踪'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return self.carrier_number


class Carrier(models.Model):
    """
    物流商
    """

    od_num = models.IntegerField(default=1,
                                 verbose_name='排序号',
                                 help_text='排序号')
    name = models.CharField(max_length=30,
                            verbose_name='物流名称',
                            help_text='物流名称')

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

    od_num = models.IntegerField(default=1,
                                 verbose_name='排序号',
                                 help_text='排序号')
    site_code = models.CharField(max_length=30,
                                 verbose_name='站点编号',
                                 help_text='站点编号')
    name = models.CharField(max_length=30,
                            verbose_name='站点名称',
                            help_text='站点名称')
    platform = models.CharField(max_length=20,
                                null=True,
                                blank=True,
                                verbose_name='平台',
                                help_text='平台')

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

    currency = models.CharField(max_length=10,
                                verbose_name='币种',
                                help_text='币种')
    value = models.FloatField(null=True,
                              blank=True,
                              default=0,
                              verbose_name='汇率',
                              help_text='汇率')
    update_time = models.DateTimeField(null=True,
                                       blank=True,
                                       verbose_name='更新时间',
                                       help_text='更新时间')

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

    country = models.CharField(max_length=30,
                               null=True,
                               blank=True,
                               verbose_name='国家',
                               help_text='国家')
    platform = models.CharField(max_length=20,
                                null=True,
                                blank=True,
                                verbose_name='平台',
                                help_text='平台')
    w_code = models.CharField(max_length=30,
                              verbose_name='仓库代码',
                              help_text='仓库代码')
    zip = models.CharField(max_length=10,
                           null=True,
                           blank=True,
                           verbose_name='邮编',
                           help_text='邮编')
    name = models.CharField(max_length=100,
                            null=True,
                            blank=True,
                            verbose_name='仓库名称',
                            help_text='仓库名称')
    address = models.CharField(max_length=300,
                               null=True,
                               blank=True,
                               verbose_name='仓库地址',
                               help_text='仓库地址')
    note = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='备注',
                            help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    is_active = models.BooleanField(default=True,
                                    verbose_name='是否启用',
                                    help_text='是否启用')

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

    shop = models.ForeignKey(Shop,
                             related_name='shop_order',
                             on_delete=models.CASCADE,
                             verbose_name='所属店铺',
                             help_text='所属店铺')
    order_number = models.CharField(max_length=30,
                                    null=True,
                                    blank=True,
                                    verbose_name='订单编号',
                                    help_text='订单编号')
    order_status = models.CharField(max_length=10,
                                    null=True,
                                    blank=True,
                                    verbose_name='订单状态',
                                    help_text='订单状态')
    order_time = models.DateTimeField(null=True,
                                      blank=True,
                                      verbose_name='订单时间',
                                      help_text='订单时间')
    order_time_bj = models.DateTimeField(null=True,
                                         blank=True,
                                         verbose_name='订单北京时间',
                                         help_text='订单北京时间')
    qty = models.IntegerField(default=0, verbose_name='数量', help_text='数量')
    currency = models.CharField(max_length=5,
                                null=True,
                                blank=True,
                                verbose_name='币种',
                                help_text='币种')
    ex_rate = models.FloatField(default=0,
                                null=True,
                                blank=True,
                                verbose_name='汇率',
                                help_text='汇率')
    price = models.FloatField(default=0,
                              null=True,
                              blank=True,
                              verbose_name='销售价',
                              help_text='销售价')
    fees = models.FloatField(default=0,
                             null=True,
                             blank=True,
                             verbose_name='佣金',
                             help_text='佣金')
    postage = models.FloatField(default=0,
                                null=True,
                                blank=True,
                                verbose_name='邮费',
                                help_text='邮费')
    receive_fund = models.FloatField(default=0,
                                     null=True,
                                     blank=True,
                                     verbose_name='收入资金',
                                     help_text='收入资金')
    profit = models.FloatField(default=0,
                               null=True,
                               blank=True,
                               verbose_name='利润rmb',
                               help_text='利润rmb')
    profit_rate = models.FloatField(default=0,
                                    null=True,
                                    blank=True,
                                    verbose_name='毛利率',
                                    help_text='毛利率')
    is_ad = models.BooleanField(default=False,
                                verbose_name='是否广告卖出',
                                help_text='是否广告卖出')
    sku = models.CharField(max_length=30,
                           verbose_name='产品SKU',
                           help_text='产品SKU')
    p_name = models.CharField(max_length=80,
                              verbose_name='产品名称',
                              help_text='产品名称')
    item_id = models.CharField(max_length=30,
                               null=True,
                               blank=True,
                               verbose_name='链接编号',
                               help_text='链接编号')
    image = models.ImageField(null=True,
                              blank=True,
                              upload_to='ml_product',
                              max_length=200,
                              verbose_name='产品图片',
                              help_text='产品图片')
    unit_cost = models.FloatField(null=True,
                                  default=0,
                                  verbose_name='均摊成本价',
                                  help_text='均摊成本价')
    first_ship_cost = models.FloatField(null=True,
                                        default=0,
                                        verbose_name='均摊头程运费',
                                        help_text='均摊头程运费')
    buyer_id = models.CharField(max_length=100,
                                null=True,
                                blank=True,
                                verbose_name='买家id',
                                help_text='买家id')
    buyer_name = models.CharField(max_length=100,
                                  null=True,
                                  blank=True,
                                  verbose_name='买家姓名',
                                  help_text='买家姓名')
    buyer_address = models.CharField(max_length=500,
                                     null=True,
                                     blank=True,
                                     verbose_name='买家街道',
                                     help_text='买家街道')
    buyer_city = models.CharField(max_length=50,
                                  null=True,
                                  blank=True,
                                  verbose_name='买家城市',
                                  help_text='买家城市')
    buyer_state = models.CharField(max_length=30,
                                   null=True,
                                   blank=True,
                                   verbose_name='买家州',
                                   help_text='买家州')
    buyer_postcode = models.CharField(max_length=20,
                                      null=True,
                                      blank=True,
                                      verbose_name='买家邮编',
                                      help_text='买家邮编')
    buyer_country = models.CharField(max_length=20,
                                     null=True,
                                     blank=True,
                                     verbose_name='买家国家',
                                     help_text='买家国家')
    shipped_date = models.DateTimeField(null=True,
                                        blank=True,
                                        verbose_name='发货时间',
                                        help_text='发货时间')
    delivered_date = models.DateTimeField(null=True,
                                          blank=True,
                                          verbose_name='送达时间',
                                          help_text='送达时间')
    VAT = models.FloatField(null=True,
                            default=0,
                            verbose_name='税价',
                            help_text='税价')
    invoice_price = models.FloatField(null=True,
                                      default=0,
                                      verbose_name='成交价',
                                      help_text='成交价')
    promo_coupon = models.FloatField(null=True,
                                     default=0,
                                     verbose_name='优惠金额',
                                     help_text='优惠金额')
    platform = models.CharField(max_length=20,
                                null=True,
                                blank=True,
                                verbose_name='平台',
                                help_text='平台')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    dispatch_number = models.CharField(max_length=30,
                                       null=True,
                                       blank=True,
                                       verbose_name='发出编号',
                                       help_text='发出编号')
    fee_rate = models.FloatField(default=0,
                                 null=True,
                                 blank=True,
                                 verbose_name='佣金率',
                                 help_text='佣金率')
    fbo_fee = models.FloatField(default=0,
                                null=True,
                                blank=True,
                                verbose_name='FBO费用',
                                help_text='FBO费用')
    last_mile_fee = models.FloatField(default=0,
                                      null=True,
                                      blank=True,
                                      verbose_name='最后一公里费用',
                                      help_text='最后一公里费用')
    payment_fee = models.FloatField(default=0,
                                    null=True,
                                    blank=True,
                                    verbose_name='收单费用',
                                    help_text='收单费用')
    finance_check1 = models.BooleanField(default=False,
                                         verbose_name='是否结算1',
                                         help_text='是否结算1')
    finance_check2 = models.BooleanField(default=False,
                                         verbose_name='是否结算2',
                                         help_text='是否结算2')
    sp_fee = models.FloatField(default=0,
                               null=True,
                               blank=True,
                               verbose_name='服务商费用',
                               help_text='服务商费用')
    sp_fee_rate = models.FloatField(default=0,
                                    null=True,
                                    blank=True,
                                    verbose_name='服务商费率',
                                    help_text='服务商费率')

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

    shop = models.ForeignKey(Shop,
                             related_name='shop_finance',
                             on_delete=models.CASCADE,
                             verbose_name='所属店铺',
                             help_text='所属店铺')
    currency = models.CharField(max_length=10,
                                null=True,
                                blank=True,
                                verbose_name='币种',
                                help_text='币种')
    income = models.FloatField(null=True,
                               default=0,
                               verbose_name='外汇收入金额',
                               help_text='外汇收入金额')
    wd_date = models.DateField(null=True,
                               blank=True,
                               verbose_name='提现日期',
                               help_text='提现日期')
    rec_date = models.DateField(null=True,
                                blank=True,
                                verbose_name='提现到账日期',
                                help_text='提现到账日期')
    exchange = models.FloatField(null=True,
                                 default=0,
                                 verbose_name='结汇金额',
                                 help_text='结汇金额')
    income_rmb = models.FloatField(null=True,
                                   default=0,
                                   verbose_name='结汇rmb',
                                   help_text='结汇rmb')
    exc_date = models.DateField(null=True,
                                blank=True,
                                verbose_name='结汇日期',
                                help_text='结汇日期')
    f_type = models.CharField(max_length=10,
                              null=True,
                              blank=True,
                              verbose_name='资金类型',
                              help_text='资金类型')
    is_received = models.BooleanField(default=False,
                                      verbose_name='外汇是否收到',
                                      help_text='外汇是否收到')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    note = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='备注',
                            help_text='备注')

    class Meta:
        verbose_name = '财务管理'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return str(self.shop)


class MLOperateLog(models.Model):
    """
    操作日志
    """

    op_module = models.CharField(max_length=10,
                                 null=True,
                                 blank=True,
                                 verbose_name='操作模块',
                                 help_text='操作模块')
    op_type = models.CharField(max_length=10,
                               null=True,
                               blank=True,
                               verbose_name='操作类型',
                               help_text='操作类型')
    target_type = models.CharField(max_length=10,
                                   null=True,
                                   blank=True,
                                   verbose_name='目标类型',
                                   help_text='目标类型')
    target_id = models.IntegerField(default=0,
                                    verbose_name='目标id',
                                    help_text='目标id')
    desc = models.CharField(max_length=300,
                            null=True,
                            blank=True,
                            verbose_name='操作描述',
                            help_text='操作描述')
    user = models.ForeignKey(User,
                             related_name='user_mlop_log',
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True,
                             verbose_name='操作人',
                             help_text='操作人')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='操作时间',
                                       help_text='操作时间')

    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return str(self.op_module)


class ShopReport(models.Model):
    """
    统计店铺每天销量
    """
    shop = models.ForeignKey(Shop,
                             null=True,
                             related_name='shop_report',
                             on_delete=models.CASCADE,
                             verbose_name='店铺',
                             help_text='店铺')
    qty = models.IntegerField(default=0, verbose_name='订单数量', help_text='订单数量')
    amount = models.FloatField(default=0.0,
                               verbose_name='销售额',
                               help_text='销售额')
    profit = models.FloatField(default=0.0,
                               verbose_name='利润rmb',
                               help_text='利润rmb')
    calc_date = models.DateField(null=True,
                                 blank=True,
                                 verbose_name='统计日期',
                                 help_text='统计日期')

    class Meta:
        verbose_name = '统计店铺每天销量'
        verbose_name_plural = verbose_name
        ordering = ['-calc_date']

    def __str__(self):
        return str(self.qty)


class PurchaseManage(models.Model):
    """
    采购管理
    """
    PRODUCT_STATUS = (
        ('WAITBUY', '待采购'),
        ('PURCHASED', '已采购'),
        ('RECEIVED', '已到货'),
        ('PACKED', '已打包'),
        ('USED', '已出库'),
    )
    p_status = models.CharField(max_length=10,
                                choices=PRODUCT_STATUS,
                                default='WAITBUY',
                                verbose_name='采购单状态',
                                help_text='采购单状态')
    platform = models.CharField(max_length=20,
                                null=True,
                                blank=True,
                                verbose_name='平台',
                                help_text='平台')
    s_type = models.CharField(max_length=10,
                              verbose_name='货品类型',
                              help_text='货品类型')
    create_type = models.CharField(max_length=10,
                                   verbose_name='创建方式',
                                   help_text='创建方式')
    sku = models.CharField(max_length=30,
                           verbose_name='产品SKU',
                           help_text='产品SKU')
    p_name = models.CharField(max_length=80,
                              verbose_name='产品名称',
                              help_text='产品名称')
    label_code = models.CharField(max_length=30,
                                  null=True,
                                  blank=True,
                                  verbose_name='FBM条码',
                                  help_text='FBM条码')
    item_id = models.CharField(max_length=30,
                               null=True,
                               blank=True,
                               verbose_name='链接编号',
                               help_text='链接编号')
    image = models.ImageField(null=True,
                              blank=True,
                              upload_to='ml_product',
                              max_length=200,
                              verbose_name='产品图片',
                              help_text='产品图片')
    unit_cost = models.FloatField(null=True,
                                  default=0,
                                  verbose_name='成本价',
                                  help_text='成本价')
    length = models.FloatField(null=True,
                               blank=True,
                               verbose_name='长cm',
                               help_text='长cm')
    width = models.FloatField(null=True,
                              blank=True,
                              verbose_name='宽cm',
                              help_text='宽cm')
    heigth = models.FloatField(null=True,
                               blank=True,
                               verbose_name='高cm',
                               help_text='高cm')
    weight = models.FloatField(null=True,
                               blank=True,
                               verbose_name='重量kg',
                               help_text='重量kg')
    buy_qty = models.IntegerField(default=0,
                                  null=True,
                                  blank=True,
                                  verbose_name='采购数量',
                                  help_text='采购数量')
    rec_qty = models.IntegerField(default=0,
                                  null=True,
                                  blank=True,
                                  verbose_name='收货数量',
                                  help_text='收货数量')
    pack_qty = models.IntegerField(default=0,
                                   null=True,
                                   blank=True,
                                   verbose_name='打包数量',
                                   help_text='打包数量')
    used_qty = models.IntegerField(default=0,
                                   null=True,
                                   blank=True,
                                   verbose_name='出库数量',
                                   help_text='出库数量')
    used_batch = models.CharField(max_length=30,
                                  null=True,
                                  blank=True,
                                  verbose_name='使用批次',
                                  help_text='使用批次')
    from_batch = models.CharField(max_length=30,
                                  null=True,
                                  blank=True,
                                  verbose_name='源批次',
                                  help_text='源批次')
    note = models.CharField(max_length=300,
                            null=True,
                            blank=True,
                            verbose_name='短备注',
                            help_text='短备注')
    shop = models.CharField(max_length=30,
                            null=True,
                            blank=True,
                            verbose_name='目标店铺',
                            help_text='目标店铺')
    shop_color = models.CharField(max_length=20,
                                  null=True,
                                  blank=True,
                                  verbose_name='店铺颜色',
                                  help_text='店铺颜色')
    packing_name = models.CharField(null=True,
                                    blank=True,
                                    max_length=80,
                                    verbose_name='包材名称',
                                    help_text='包材名称')
    packing_size = models.CharField(null=True,
                                    blank=True,
                                    max_length=80,
                                    verbose_name='包材尺寸',
                                    help_text='包材尺寸')
    create_time = models.DateTimeField(null=True,
                                       blank=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    buy_time = models.DateTimeField(null=True,
                                    blank=True,
                                    verbose_name='采购时间',
                                    help_text='采购时间')
    rec_time = models.DateTimeField(null=True,
                                    blank=True,
                                    verbose_name='到货时间',
                                    help_text='到货时间')
    pack_time = models.DateTimeField(null=True,
                                     blank=True,
                                     verbose_name='打包时间',
                                     help_text='打包时间')
    used_time = models.DateTimeField(null=True,
                                     blank=True,
                                     verbose_name='出库时间',
                                     help_text='出库时间')
    location = models.CharField(max_length=30,
                                null=True,
                                blank=True,
                                verbose_name='仓位',
                                help_text='仓位')
    is_urgent = models.BooleanField(default=False,
                                    verbose_name='是否紧急',
                                    help_text='是否紧急')
    is_qc = models.BooleanField(default=False,
                                verbose_name='是否质检',
                                help_text='是否质检')

    class Meta:
        verbose_name = '采购管理'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.sku


class UPC(models.Model):
    """
    UPC号码池
    """

    number = models.CharField(max_length=50,
                              null=True,
                              blank=True,
                              verbose_name='upc号码',
                              help_text='upc号码')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='生成时间',
                                       help_text='生成时间')
    use_time = models.DateTimeField(null=True,
                                    blank=True,
                                    verbose_name='使用时间',
                                    help_text='使用时间')
    is_used = models.BooleanField(default=False,
                                  verbose_name='是否使用',
                                  help_text='是否使用')
    user = models.ForeignKey(User,
                             related_name='user_upc',
                             on_delete=models.SET_NULL,
                             null=True,
                             blank=True,
                             verbose_name='user',
                             help_text='user')

    class Meta:
        verbose_name = 'UPC号码池'
        verbose_name_plural = verbose_name
        ordering = ['-use_time']

    def __str__(self):
        return self.number


class RefillRecommend(models.Model):
    """
    补货推荐
    """
    shop = models.ForeignKey(Shop,
                             null=True,
                             related_name='shop_refill',
                             on_delete=models.CASCADE,
                             verbose_name='店铺',
                             help_text='店铺')
    sku = models.CharField(max_length=30,
                           verbose_name='产品SKU',
                           help_text='产品SKU')
    p_name = models.CharField(max_length=80,
                              verbose_name='产品名称',
                              help_text='产品名称')
    image = models.ImageField(null=True,
                              blank=True,
                              upload_to='ml_product',
                              max_length=200,
                              verbose_name='产品图片',
                              help_text='产品图片')
    item_id = models.CharField(max_length=30,
                               null=True,
                               blank=True,
                               verbose_name='链接编号',
                               help_text='链接编号')
    is_new = models.BooleanField(default=False,
                                 verbose_name='是否新品',
                                 help_text='是否新品')
    first_list_days = models.IntegerField(default=0,
                                          verbose_name='首次上架天数',
                                          help_text='首次上架天数')
    trend = models.CharField(max_length=10,
                             null=True,
                             blank=True,
                             verbose_name='销量趋势',
                             help_text='销量趋势')
    all_sold = models.IntegerField(default=0,
                                   verbose_name='总销量',
                                   help_text='总销量')
    days30_sold = models.IntegerField(default=0,
                                      verbose_name='30天销量',
                                      help_text='30天销量')
    days15_sold = models.IntegerField(default=0,
                                      verbose_name='15天销量',
                                      help_text='15天销量')
    days7_sold = models.IntegerField(default=0,
                                     verbose_name='7天销量',
                                     help_text='7天销量')
    fbm_qty = models.IntegerField(default=0,
                                  verbose_name='fbm库存数量',
                                  help_text='fbm库存数量')
    onway_qty = models.IntegerField(default=0,
                                    verbose_name='在途数量',
                                    help_text='在途数量')
    trans_qty = models.IntegerField(default=0,
                                    verbose_name='中转仓数量',
                                    help_text='中转仓数量')
    trans_onway_qty = models.IntegerField(default=0,
                                          verbose_name='中转在途数量',
                                          help_text='中转在途数量')
    prepare_qty = models.IntegerField(default=0,
                                      verbose_name='备货中数量',
                                      help_text='备货中数量')
    own_qty = models.IntegerField(default=0,
                                  verbose_name='现货数量',
                                  help_text='现货数量')
    avg_sale = models.FloatField(default=0.0,
                                 verbose_name='日均销量',
                                 help_text='日均销量')
    keep_days = models.IntegerField(default=0,
                                    verbose_name='库存维持天数',
                                    help_text='库存维持天数')
    min_send = models.IntegerField(default=0,
                                   verbose_name='最低发货数量',
                                   help_text='最低发货数量')
    full_send = models.IntegerField(default=0,
                                    verbose_name='完整周期发货数量',
                                    help_text='完整周期发货数量')
    advice = models.CharField(max_length=50,
                              null=True,
                              blank=True,
                              verbose_name='建议注释',
                              help_text='建议注释')
    create_time = models.DateTimeField(null=True,
                                       blank=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')

    class Meta:
        verbose_name = '补货推荐'
        verbose_name_plural = verbose_name
        ordering = ['item_id']

    def __str__(self):
        return self.sku


class RefillSettings(models.Model):
    """
    补货推荐设置
    """
    fly_days = models.IntegerField(default=0,
                                   verbose_name='空运物流及上架时间',
                                   help_text='空运物流及上架时间')
    sea_days = models.IntegerField(default=0,
                                   verbose_name='海运物流及上架时间',
                                   help_text='海运物流及上架时间')
    fly_batch_period = models.IntegerField(default=0,
                                           verbose_name='空运批次周期',
                                           help_text='空运批次周期')
    sea_batch_period = models.IntegerField(default=0,
                                           verbose_name='海运批次周期',
                                           help_text='海运批次周期')
    is_include_trans = models.BooleanField(default=True,
                                           verbose_name='是否包含中转仓数量',
                                           help_text='是否包含中转仓数量')
    platform = models.CharField(max_length=20,
                                null=True,
                                blank=True,
                                verbose_name='平台',
                                help_text='平台')

    class Meta:
        verbose_name = '补货推荐设置'
        verbose_name_plural = verbose_name
        ordering = ['fly_days']

    def __str__(self):
        return str(self.fly_days)


class FileUploadNotify(models.Model):
    """
    文件上传通知
    """
    shop = models.ForeignKey(Shop,
                             null=True,
                             related_name='shop_file_upload',
                             on_delete=models.CASCADE,
                             verbose_name='店铺',
                             help_text='店铺')
    upload_status = models.CharField(max_length=10,
                                     verbose_name='上传状态',
                                     help_text='上传状态')
    upload_type = models.CharField(max_length=10,
                                   verbose_name='上传类型',
                                   help_text='上传类型')
    desc = models.CharField(max_length=100,
                            null=True,
                            blank=True,
                            verbose_name='描述',
                            help_text='描述')
    user_id = models.IntegerField(default=0,
                                  null=True,
                                  blank=True,
                                  verbose_name='操作人id',
                                  help_text='操作人id')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')

    class Meta:
        verbose_name = '文件上传通知'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.upload_status


class GeneralSettings(models.Model):
    """
    通用数据设置
    """

    item_name = models.CharField(max_length=10,
                                 verbose_name='项目名称',
                                 help_text='项目名称')
    update_time = models.DateTimeField(null=True,
                                       blank=True,
                                       verbose_name='更新时间',
                                       help_text='更新时间')
    text1 = models.CharField(max_length=50,
                             null=True,
                             blank=True,
                             verbose_name='文本字段1',
                             help_text='文本字段1')
    text2 = models.CharField(max_length=50,
                             null=True,
                             blank=True,
                             verbose_name='文本字段2',
                             help_text='文本字段2')
    text3 = models.CharField(max_length=50,
                             null=True,
                             blank=True,
                             verbose_name='文本字段3',
                             help_text='文本字段3')
    value1 = models.FloatField(null=True,
                               blank=True,
                               verbose_name='浮点字段1',
                               help_text='浮点字段1')
    value2 = models.FloatField(null=True,
                               blank=True,
                               verbose_name='浮点字段2',
                               help_text='浮点字段2')
    value3 = models.FloatField(null=True,
                               blank=True,
                               verbose_name='浮点字段3',
                               help_text='浮点字段3')
    num1 = models.IntegerField(default=0,
                               null=True,
                               blank=True,
                               verbose_name='整数字段1',
                               help_text='整数字段1')
    num2 = models.IntegerField(default=0,
                               null=True,
                               blank=True,
                               verbose_name='整数字段2',
                               help_text='整数字段2')
    num3 = models.IntegerField(default=0,
                               null=True,
                               blank=True,
                               verbose_name='整数字段3',
                               help_text='整数字段3')
    sw1 = models.BooleanField(default=False,
                              verbose_name='开关字段1',
                              help_text='开关字段1')
    sw2 = models.BooleanField(default=False,
                              verbose_name='开关字段2',
                              help_text='开关字段2')
    sw3 = models.BooleanField(default=False,
                              verbose_name='开关字段3',
                              help_text='开关字段3')
    d1 = models.DateTimeField(null=True,
                              blank=True,
                              verbose_name='日期字段1',
                              help_text='日期字段1')
    d2 = models.DateTimeField(null=True,
                              blank=True,
                              verbose_name='日期字段2',
                              help_text='日期字段2')
    d3 = models.DateTimeField(null=True,
                              blank=True,
                              verbose_name='日期字段3',
                              help_text='日期字段3')
    note = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='备注',
                            help_text='备注')

    class Meta:
        verbose_name = '通用数据设置'
        verbose_name_plural = verbose_name
        ordering = ['update_time']

    def __str__(self):
        return self.item_name


class PlatformCategoryRate(models.Model):
    """
    平台类目佣金费率
    """

    platform = models.CharField(max_length=10,
                                verbose_name='平台名称',
                                help_text='平台名称')
    site = models.CharField(max_length=10,
                            verbose_name='站点名称',
                            help_text='站点名称')
    category_id = models.CharField(max_length=30,
                                   null=True,
                                   blank=True,
                                   verbose_name='类目id',
                                   help_text='类目id')
    en_name = models.CharField(max_length=80,
                               null=True,
                               blank=True,
                               verbose_name='英文类目名称',
                               help_text='英文类目名称')
    cn_name = models.CharField(max_length=80,
                               null=True,
                               blank=True,
                               verbose_name='中文类目名称',
                               help_text='中文类目名称')
    first_category = models.CharField(max_length=80,
                                      null=True,
                                      blank=True,
                                      verbose_name='一级目录',
                                      help_text='一级目录')
    fixed_fee0 = models.FloatField(null=True,
                                   blank=True,
                                   verbose_name='固定费用(无店铺)',
                                   help_text='固定费用(无店铺)')
    fixed_fee1 = models.FloatField(null=True,
                                   blank=True,
                                   verbose_name='固定费用(有店铺)',
                                   help_text='固定费用(有店铺)')
    fee0 = models.FloatField(null=True,
                             blank=True,
                             verbose_name='无店铺佣金',
                             help_text='无店铺佣金')
    fee1 = models.FloatField(null=True,
                             blank=True,
                             verbose_name='初级店铺佣金',
                             help_text='初级店铺佣金')
    fee2 = models.FloatField(null=True,
                             blank=True,
                             verbose_name='中级店铺佣金',
                             help_text='中级店铺佣金')
    fee3 = models.FloatField(null=True,
                             blank=True,
                             verbose_name='高级店铺佣金',
                             help_text='高级店铺佣金')

    class Meta:
        verbose_name = '平台类目佣金费率'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.en_name


class ShippingPrice(models.Model):
    """
    虚拟仓物流价格
    """

    country = models.CharField(max_length=10,
                               verbose_name='国家',
                               help_text='国家')
    carrier_name = models.CharField(max_length=50,
                                    null=True,
                                    blank=True,
                                    verbose_name='物流名称',
                                    help_text='物流名称')
    carrier_code = models.CharField(max_length=30,
                                    null=True,
                                    blank=True,
                                    verbose_name='物流代码',
                                    help_text='物流代码')
    area = models.CharField(max_length=30,
                            null=True,
                            blank=True,
                            verbose_name='分区',
                            help_text='分区')
    basic_price = models.FloatField(null=True,
                                    blank=True,
                                    verbose_name='基础价格',
                                    help_text='基础价格')
    calc_price = models.FloatField(null=True,
                                   blank=True,
                                   verbose_name='计算价格',
                                   help_text='计算价格')
    volume_ratio = models.IntegerField(null=True,
                                       blank=True,
                                       verbose_name='体积计算率',
                                       help_text='体积计算率')
    min_weight = models.IntegerField(null=True,
                                     blank=True,
                                     verbose_name='区间最小重量g',
                                     help_text='区间最小重量g')
    max_weight = models.IntegerField(null=True,
                                     blank=True,
                                     verbose_name='区间最大重量g',
                                     help_text='区间最大重量g')
    is_elec = models.BooleanField(default=False,
                                  verbose_name='是否带电',
                                  help_text='是否带电')

    class Meta:
        verbose_name = '虚拟仓物流价格'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.carrier_name


class ShippingAreaCode(models.Model):
    """
    物流服务分区
    """

    country = models.CharField(max_length=10,
                               verbose_name='国家',
                               help_text='国家')
    carrier_name = models.CharField(max_length=50,
                                    null=True,
                                    blank=True,
                                    verbose_name='物流名称',
                                    help_text='物流名称')
    carrier_code = models.CharField(max_length=30,
                                    null=True,
                                    blank=True,
                                    verbose_name='物流代码',
                                    help_text='物流代码')
    postcode = models.CharField(max_length=10,
                                verbose_name='邮编',
                                help_text='邮编')
    area = models.CharField(max_length=30,
                            null=True,
                            blank=True,
                            verbose_name='分区',
                            help_text='分区')
    is_avaiable = models.BooleanField(default=True,
                                      verbose_name='配送服务',
                                      help_text='配送服务')
    note = models.CharField(max_length=100,
                            null=True,
                            blank=True,
                            verbose_name='简要备注',
                            help_text='简要备注')
    update_time = models.DateTimeField(null=True,
                                       blank=True,
                                       verbose_name='更新时间',
                                       help_text='更新时间')

    class Meta:
        verbose_name = '物流服务分区'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.postcode
