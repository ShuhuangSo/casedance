from django.db import models


# Create your models here.
class DevProduct(models.Model):
    """
    产品开发列表
    """

    sku = models.CharField(max_length=30,
                           null=True,
                           blank=True,
                           verbose_name='产品SKU',
                           help_text='产品SKU')
    cn_name = models.CharField(max_length=100,
                               null=True,
                               blank=True,
                               verbose_name='产品中文名称',
                               help_text='产品中文名称')
    en_name = models.CharField(max_length=100,
                               null=True,
                               blank=True,
                               verbose_name='产品英文名称',
                               help_text='产品英文名称')
    image = models.ImageField(null=True,
                              blank=True,
                              upload_to='dev_product',
                              max_length=200,
                              verbose_name='产品图片',
                              help_text='产品图片')
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
    is_dust = models.BooleanField(default=False,
                                  null=True,
                                  verbose_name='是否粉末',
                                  help_text='是否粉末')
    is_confirm_data = models.BooleanField(default=False,
                                          null=True,
                                          verbose_name='是否确认重量尺寸',
                                          help_text='是否确认重量尺寸')
    is_stock = models.BooleanField(default=False,
                                   null=True,
                                   verbose_name='是否有库存',
                                   help_text='是否有库存')
    keywords = models.CharField(max_length=100,
                                null=True,
                                blank=True,
                                verbose_name='搜索关键词',
                                help_text='搜索关键词')
    category = models.CharField(max_length=100,
                                null=True,
                                blank=True,
                                verbose_name='产品分类',
                                help_text='产品分类')
    package_included = models.CharField(max_length=500,
                                        null=True,
                                        blank=True,
                                        verbose_name='产品清单',
                                        help_text='产品清单')
    unit_cost = models.FloatField(null=True,
                                  blank=True,
                                  verbose_name='成本价',
                                  help_text='成本价')
    p_length = models.FloatField(null=True,
                                 blank=True,
                                 verbose_name='长cm',
                                 help_text='长cm')
    p_width = models.FloatField(null=True,
                                blank=True,
                                verbose_name='宽cm',
                                help_text='宽cm')
    p_height = models.FloatField(null=True,
                                 blank=True,
                                 verbose_name='高cm',
                                 help_text='高cm')
    p_weight = models.FloatField(null=True,
                                 blank=True,
                                 verbose_name='重量g',
                                 help_text='重量g')
    buy_url1 = models.CharField(null=True,
                                blank=True,
                                max_length=500,
                                verbose_name='产品采购链接1',
                                help_text='产品采购链接1')
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
    refer_url1 = models.CharField(null=True,
                                  blank=True,
                                  max_length=500,
                                  verbose_name='参考链接1',
                                  help_text='参考链接1')
    refer_url2 = models.CharField(null=True,
                                  blank=True,
                                  max_length=500,
                                  verbose_name='参考链接2',
                                  help_text='参考链接2')
    desc = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='产品描述',
                            help_text='产品描述')
    note = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='备注',
                            help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    online_time = models.DateTimeField(null=True,
                                       blank=True,
                                       verbose_name='发布时间',
                                       help_text='发布时间')
    offline_time = models.DateTimeField(null=True,
                                        blank=True,
                                        verbose_name='下架时间',
                                        help_text='下架时间')
    user_id = models.IntegerField(default=0,
                                  null=True,
                                  blank=True,
                                  verbose_name='创建人id',
                                  help_text='创建人id')
    qty = models.IntegerField(null=True,
                              blank=True,
                              verbose_name='库存数量',
                              help_text='库存数量')
    percent = models.IntegerField(null=True,
                                  blank=True,
                                  verbose_name='上架完成百分比',
                                  help_text='上架完成百分比')
    rate = models.IntegerField(null=True,
                               blank=True,
                               default=0,
                               verbose_name='产品评分',
                               help_text='产品评分')
    p_status = models.CharField(max_length=15,
                                null=True,
                                blank=True,
                                verbose_name='状态',
                                help_text='状态')
    buy_status = models.CharField(max_length=15,
                                  null=True,
                                  blank=True,
                                  verbose_name='备货状态',
                                  help_text='备货状态')
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
    cp_id = models.IntegerField(null=True,
                                blank=True,
                                verbose_name='关联识别码',
                                help_text='关联识别码')
    local_category = models.IntegerField(null=True,
                                         blank=True,
                                         default=0,
                                         verbose_name='产品目录',
                                         help_text='产品目录')
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
    total_profit = models.FloatField(null=True,
                                     blank=True,
                                     verbose_name='累计利润',
                                     help_text='累计利润')
    avg_profit = models.FloatField(null=True,
                                   blank=True,
                                   verbose_name='平均毛利润',
                                   help_text='平均毛利润')
    avg_profit_rate = models.FloatField(null=True,
                                        blank=True,
                                        verbose_name='平均毛利率',
                                        help_text='平均毛利率')

    class Meta:
        verbose_name = '产品开发列表'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.cn_name


class DevPrice(models.Model):
    """
    产品开发定价
    """
    dev_p = models.ForeignKey(DevProduct,
                              related_name='dev_price',
                              on_delete=models.CASCADE,
                              verbose_name='所属开发产品',
                              help_text='所属开发产品')
    platform = models.CharField(max_length=20,
                                null=True,
                                blank=True,
                                verbose_name='平台',
                                help_text='平台')
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
    price = models.FloatField(default=0,
                              null=True,
                              blank=True,
                              verbose_name='定价',
                              help_text='定价')
    profit = models.FloatField(default=0,
                               null=True,
                               blank=True,
                               verbose_name='毛利润',
                               help_text='毛利润')
    gross_margin = models.FloatField(default=0,
                                     null=True,
                                     blank=True,
                                     verbose_name='毛利率',
                                     help_text='毛利率')
    ex_rate = models.FloatField(default=0,
                                null=True,
                                blank=True,
                                verbose_name='汇率',
                                help_text='汇率')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    update_time = models.DateTimeField(null=True,
                                       blank=True,
                                       verbose_name='更新时间',
                                       help_text='更新时间')
    note = models.TextField(null=True,
                            blank=True,
                            default='',
                            verbose_name='备注',
                            help_text='备注')
    upc = models.CharField(max_length=30,
                           null=True,
                           blank=True,
                           verbose_name='UPC',
                           help_text='UPC')
    custom_code = models.CharField(null=True,
                                   blank=True,
                                   max_length=20,
                                   verbose_name='海关编码',
                                   help_text='海关编码')
    custom_cn_name = models.CharField(null=True,
                                      blank=True,
                                      max_length=30,
                                      verbose_name='申报中文品名',
                                      help_text='申报中文品名')
    custom_en_name = models.CharField(null=True,
                                      blank=True,
                                      max_length=30,
                                      verbose_name='申报英文品名',
                                      help_text='申报英文品名')
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

    class Meta:
        verbose_name = '产品开发定价'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return self.platform


class DevListingChannel(models.Model):
    """
    开发产品发布渠道
    """
    dev_p = models.ForeignKey(DevProduct,
                              related_name='dev_listing_channel',
                              on_delete=models.CASCADE,
                              verbose_name='所属开发产品',
                              help_text='所属开发产品')
    platform = models.CharField(max_length=20,
                                null=True,
                                blank=True,
                                verbose_name='平台',
                                help_text='平台')
    site = models.CharField(max_length=20,
                            null=True,
                            blank=True,
                            verbose_name='站点',
                            help_text='站点')
    include_china = models.BooleanField(default=False,
                                        null=True,
                                        verbose_name='包含跨境号',
                                        help_text='包含跨境号')
    is_active = models.BooleanField(default=True,
                                    verbose_name='是否启用',
                                    help_text='是否启用')

    class Meta:
        verbose_name = '开发产品发布渠道'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.platform


class DevListingAccount(models.Model):
    """
    开发产品上架账号
    """
    dev_p = models.ForeignKey(DevProduct,
                              related_name='dev_listing_account',
                              on_delete=models.CASCADE,
                              verbose_name='所属开发产品',
                              help_text='所属开发产品')
    platform = models.CharField(max_length=20,
                                null=True,
                                blank=True,
                                verbose_name='平台',
                                help_text='平台')
    site = models.CharField(max_length=20,
                            null=True,
                            blank=True,
                            verbose_name='站点',
                            help_text='站点')
    ac_type = models.CharField(null=True,
                               blank=True,
                               default='CHINA',
                               max_length=10,
                               verbose_name='账号类型',
                               help_text='账号类型')
    account_name = models.CharField(max_length=50,
                                    null=True,
                                    blank=True,
                                    verbose_name='账号名称',
                                    help_text='账号名称')
    user_id = models.IntegerField(default=0,
                                  null=True,
                                  blank=True,
                                  verbose_name='负责人id',
                                  help_text='负责人id')
    user_name = models.CharField(max_length=20,
                                 null=True,
                                 blank=True,
                                 verbose_name='负责姓名',
                                 help_text='负责姓名')
    item_id = models.CharField(max_length=30,
                               null=True,
                               blank=True,
                               verbose_name='产品在线id',
                               help_text='产品在线id')
    is_online = models.BooleanField(default=False,
                                    null=True,
                                    verbose_name='是否已上架',
                                    help_text='是否已上架')
    online_time = models.DateTimeField(null=True,
                                       blank=True,
                                       verbose_name='上架时间',
                                       help_text='上架时间')
    offline_time = models.DateTimeField(null=True,
                                        blank=True,
                                        verbose_name='下架时间',
                                        help_text='下架时间')
    note = models.CharField(max_length=200,
                            null=True,
                            blank=True,
                            verbose_name='备注',
                            help_text='备注')
    notify = models.IntegerField(default=0,
                                 null=True,
                                 blank=True,
                                 verbose_name='通知标记',
                                 help_text='通知标记')
    is_paused = models.BooleanField(default=False,
                                    null=True,
                                    verbose_name='是否暂停',
                                    help_text='是否暂停')
    create_time = models.DateTimeField(auto_now_add=True,
                                       null=True,
                                       blank=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')
    total_sold = models.IntegerField(default=0,
                                     verbose_name='累计销量',
                                     help_text='累计销量')

    # create_time.editable = True

    class Meta:
        verbose_name = '开发产品上架账号'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.account_name


class DevChannelData(models.Model):
    """
    开发平台渠道数据
    """
    platform = models.CharField(max_length=20,
                                null=True,
                                blank=True,
                                verbose_name='平台',
                                help_text='平台')
    site = models.CharField(max_length=20,
                            null=True,
                            blank=True,
                            verbose_name='站点',
                            help_text='站点')
    include_china = models.BooleanField(default=False,
                                        null=True,
                                        verbose_name='包含跨境号',
                                        help_text='包含跨境号')
    default_active = models.BooleanField(default=False,
                                         null=True,
                                         verbose_name='是否默认激活',
                                         help_text='是否默认激活')
    create_time = models.DateTimeField(auto_now_add=True,
                                       verbose_name='创建时间',
                                       help_text='创建时间')

    class Meta:
        verbose_name = '开发平台渠道数据'
        verbose_name_plural = verbose_name
        ordering = ['create_time']

    def __str__(self):
        return self.platform


class DevOrder(models.Model):
    """
    开发产品订单
    """

    dev_p_id = models.IntegerField(null=True,
                                   blank=True,
                                   verbose_name='开发产品id',
                                   help_text='开发产品id')
    platform = models.CharField(max_length=20,
                                null=True,
                                blank=True,
                                verbose_name='平台',
                                help_text='平台')
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
    sku = models.CharField(max_length=30,
                           null=True,
                           blank=True,
                           verbose_name='产品SKU',
                           help_text='产品SKU')
    cn_name = models.CharField(max_length=100,
                               null=True,
                               blank=True,
                               verbose_name='产品中文名称',
                               help_text='产品中文名称')
    image = models.ImageField(null=True,
                              blank=True,
                              max_length=200,
                              verbose_name='产品图片',
                              help_text='产品图片')
    account_name = models.CharField(max_length=50,
                                    null=True,
                                    blank=True,
                                    verbose_name='账号名称',
                                    help_text='账号名称')
    item_id = models.CharField(max_length=30,
                               null=True,
                               blank=True,
                               verbose_name='产品在线id',
                               help_text='产品在线id')
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
    qty = models.IntegerField(default=0, verbose_name='数量', help_text='数量')
    ex_rate = models.FloatField(default=0,
                                null=True,
                                blank=True,
                                verbose_name='汇率',
                                help_text='汇率')
    item_price = models.FloatField(default=0,
                                   null=True,
                                   blank=True,
                                   verbose_name='销售单价',
                                   help_text='销售单价')
    postage_price = models.FloatField(default=0,
                                      null=True,
                                      blank=True,
                                      verbose_name='收取运费',
                                      help_text='收取运费')
    total_price = models.FloatField(default=0,
                                    null=True,
                                    blank=True,
                                    verbose_name='销售总价',
                                    help_text='销售总价')
    fees = models.FloatField(default=0,
                             null=True,
                             blank=True,
                             verbose_name='佣金',
                             help_text='佣金')
    postage = models.FloatField(default=0,
                                null=True,
                                blank=True,
                                verbose_name='发货邮费',
                                help_text='发货邮费')
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
    ad_fee = models.FloatField(default=0,
                               null=True,
                               blank=True,
                               verbose_name='广告费',
                               help_text='广告费')
    is_combined = models.BooleanField(default=False,
                                      verbose_name='是否合并订单',
                                      help_text='是否合并订单')
    is_settled = models.BooleanField(default=False,
                                     verbose_name='是否已结算',
                                     help_text='是否已结算')
    is_resent = models.BooleanField(default=False,
                                    verbose_name='是否重发订单',
                                    help_text='是否重发订单')
    unit_cost = models.FloatField(null=True,
                                  blank=True,
                                  verbose_name='成本价',
                                  help_text='成本价')

    class Meta:
        verbose_name = '开发产品订单'
        verbose_name_plural = verbose_name
        ordering = ['order_time']

    def __str__(self):
        return self.order_number
