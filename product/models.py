from django.db import models

from setting.models import Tag


# Create your models here.


class Product(models.Model):
    """
    产品库
    """
    PRODUCT_STATUS = (
        ('ON_SALE', '在售'),
        ('OFFLINE', '停售'),
        ('CLEAN', '清仓中'),
        ('UN_LISTED', '未上市'),
        ('PRIVATE', '私模'),
    )
    STRATEGY = (
        ('RADICAL', '激进'),
        ('STANDARD', '标准'),
        ('CONSERVE', '保守'),
    )

    sku = models.CharField(max_length=30, verbose_name='产品SKU', help_text='产品SKU')
    p_name = models.CharField(max_length=80, verbose_name='产品名称', help_text='产品名称')
    label_name = models.CharField(max_length=30, null=True, blank=True, verbose_name='条码标签名', help_text='条码标签名')
    image = models.ImageField(null=True, blank=True, upload_to='product_image', max_length=200, verbose_name='产品图片',
                              help_text='产品图片')
    status = models.CharField(max_length=10, choices=PRODUCT_STATUS, default='UN_LISTED', verbose_name='产品状态',
                              help_text='产品状态')
    brand = models.CharField(null=True, blank=True, max_length=20, verbose_name='品牌', help_text='品牌')
    series = models.CharField(null=True, blank=True, max_length=30, verbose_name='产品系列', help_text='产品系列')
    p_type = models.CharField(null=True, blank=True, max_length=30, verbose_name='产品类型', help_text='产品类型')
    unit_cost = models.FloatField(null=True, blank=True, verbose_name='成本价', help_text='成本价')
    sale_price = models.FloatField(null=True, blank=True, verbose_name='销售定价', help_text='销售定价')
    length = models.FloatField(null=True, blank=True, verbose_name='长cm', help_text='长cm')
    width = models.FloatField(null=True, blank=True, verbose_name='宽cm', help_text='宽cm')
    heigth = models.FloatField(null=True, blank=True, verbose_name='高cm', help_text='高cm')
    weight = models.FloatField(null=True, blank=True, verbose_name='重量kg', help_text='重量kg')
    url = models.CharField(null=True, blank=True, max_length=200, verbose_name='商品URL', help_text='商品URL')
    is_auto_promote = models.BooleanField(default=True, verbose_name='是否补货推荐', help_text='是否补货推荐')
    stock_strategy = models.CharField(max_length=10, choices=STRATEGY, default='STANDARD', verbose_name='备货策略',
                                      help_text='备货策略')
    stock_days = models.IntegerField(default=0, null=True, blank=True, verbose_name='备货天数', help_text='备货天数')
    alert_qty = models.IntegerField(default=0, null=True, blank=True, verbose_name='警戒库存', help_text='警戒库存')
    alert_days = models.IntegerField(default=0, null=True, blank=True, verbose_name='警戒天数', help_text='警戒天数')
    mini_pq = models.IntegerField(default=0, null=True, blank=True, verbose_name='最小采购量', help_text='最小采购量')
    max_pq = models.IntegerField(default=0, null=True, blank=True, verbose_name='采购上限', help_text='采购上限')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '产品库'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.sku


class ProductExtraInfo(models.Model):
    """
    产品附属信息
    """
    INFO_TYPE = (
        ('BRAND', '品牌'),
        ('SERIES', '系列'),
        ('P_TYPE', '产品类型'),
    )

    type = models.CharField(max_length=10, choices=INFO_TYPE, default='SERIES', verbose_name='信息类型',
                            help_text='信息类型')
    name = models.CharField(max_length=30, verbose_name='信息名称', help_text='信息名称')

    class Meta:
        verbose_name = '产品附属信息'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.name


class DeviceModel(models.Model):
    """
    市面手机型号表
    """

    brand = models.CharField(null=True, blank=True, max_length=20, verbose_name='品牌', help_text='品牌')
    type = models.CharField(null=True, blank=True, max_length=20, verbose_name='类型', help_text='类型')
    model = models.CharField(max_length=40, verbose_name='型号', help_text='型号')
    cp_id = models.IntegerField(null=True, blank=True, verbose_name='兼容识别码', help_text='兼容识别码')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    image = models.CharField(null=True, blank=True, max_length=250, verbose_name='型号图片', help_text='型号图片')
    dimensions = models.CharField(null=True, blank=True, max_length=50, verbose_name='尺寸', help_text='尺寸')
    weight = models.CharField(null=True, blank=True, max_length=50, verbose_name='重量', help_text='重量')
    link = models.CharField(null=True, blank=True, max_length=150, verbose_name='链接', help_text='链接')
    announced = models.CharField(null=True, blank=True, max_length=50, verbose_name='发布时间', help_text='发布时间')
    status = models.CharField(null=True, blank=True, max_length=50, verbose_name='状态', help_text='状态')
    create_time = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '市面手机型号表'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.model


class DeviceBrand(models.Model):
    brand_name = models.CharField(max_length=30, verbose_name='品牌名称', help_text='品牌名称')
    link = models.CharField(max_length=150, verbose_name='链接', help_text='链接')

    class Meta:
        verbose_name = '市面手机品牌'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return self.brand_name


class CompatibleModel(models.Model):
    """
    产品兼容手机型号
    """

    product = models.ForeignKey(Product, related_name='product_comp_model', on_delete=models.DO_NOTHING,
                                verbose_name='产品', help_text='产品')
    phone_model = models.ForeignKey(DeviceModel, related_name='device_comp_model', on_delete=models.DO_NOTHING,
                                    verbose_name='市面手机型号', help_text='市面手机型号')

    class Meta:
        verbose_name = '产品兼容手机型号'
        verbose_name_plural = verbose_name
        ordering = ['phone_model']

    def __str__(self):
        return str(self.id)


class ProductTag(models.Model):
    """
    产品标签表
    """

    product = models.ForeignKey(Product, related_name='product_p_tag', on_delete=models.CASCADE, verbose_name='产品',
                                help_text='产品')
    tag = models.ForeignKey(Tag, related_name='tag_p_tag', on_delete=models.CASCADE, verbose_name='标签', help_text='标签')

    class Meta:
        verbose_name = '产品标签表'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return str(self.tag)


class Supplier(models.Model):
    """
    供应商
    """
    WAY = (
        ('FACTORY', '工厂'),
        ('1688', '1688'),
        ('OTHERS', '其它'),
    )

    supplier_name = models.CharField(max_length=80, verbose_name='供应商名称', help_text='供应商名称')
    buy_way = models.CharField(max_length=10, choices=WAY, default='FACTORY', verbose_name='采购渠道',
                               help_text='采购渠道')
    address = models.CharField(null=True, blank=True, max_length=200, verbose_name='地址', help_text='地址')
    contact_name = models.CharField(null=True, blank=True, max_length=20, verbose_name='联系人', help_text='联系人')
    phone = models.CharField(null=True, blank=True, max_length=15, verbose_name='电话', help_text='电话')
    qq = models.CharField(null=True, blank=True, max_length=15, verbose_name='QQ', help_text='QQ')
    wechat = models.CharField(null=True, blank=True, max_length=15, verbose_name='微信', help_text='微信')
    email = models.CharField(null=True, blank=True, max_length=50, verbose_name='邮箱', help_text='邮箱')
    is_active = models.BooleanField(default=True, verbose_name='状态', help_text='状态')
    note = models.TextField(null=True, blank=True, default='', verbose_name='备注', help_text='备注')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间')

    class Meta:
        verbose_name = '供应商'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

    def __str__(self):
        return self.supplier_name

