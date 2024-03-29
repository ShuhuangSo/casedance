# Generated by Django 3.2.4 on 2022-11-18 18:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0021_mlproduct'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('warehouse_type', models.CharField(help_text='仓库类型', max_length=30, verbose_name='仓库类型')),
                ('name', models.CharField(help_text='店铺代号', max_length=30, verbose_name='店铺代号')),
                ('shop_type', models.CharField(help_text='店铺类型', max_length=30, verbose_name='店铺类型')),
                ('seller_id', models.CharField(blank=True, help_text='店铺ID', max_length=30, null=True, verbose_name='店铺ID')),
                ('nickname', models.CharField(blank=True, help_text='店铺名称', max_length=50, null=True, verbose_name='店铺名称')),
                ('site', models.CharField(blank=True, help_text='站点', max_length=20, null=True, verbose_name='站点')),
                ('url', models.CharField(blank=True, help_text='店铺链接', max_length=300, null=True, verbose_name='店铺链接')),
                ('note', models.TextField(blank=True, default='', help_text='备注', null=True, verbose_name='备注')),
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('is_active', models.BooleanField(default=True, help_text='是否启用', verbose_name='是否启用')),
                ('total_profit', models.FloatField(blank=True, help_text='累计利润', null=True, verbose_name='累计利润')),
                ('total_weight', models.FloatField(blank=True, help_text='库存总重量kg', null=True, verbose_name='库存总重量kg')),
                ('total_cbm', models.FloatField(blank=True, help_text='库存总体积cbm', null=True, verbose_name='库存总体积cbm')),
                ('stock_value', models.FloatField(blank=True, help_text='库存价值rmb', null=True, verbose_name='库存价值rmb')),
                ('total_qty', models.IntegerField(blank=True, help_text='库存价值rmb', null=True, verbose_name='库存价值rmb')),
            ],
            options={
                'verbose_name': 'FBM店铺',
                'verbose_name_plural': 'FBM店铺',
                'ordering': ['-create_time'],
            },
        ),
        migrations.CreateModel(
            name='ShopStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(help_text='产品SKU', max_length=30, verbose_name='产品SKU')),
                ('p_name', models.CharField(help_text='产品名称', max_length=80, verbose_name='产品名称')),
                ('label_code', models.CharField(blank=True, help_text='FBM条码', max_length=30, null=True, verbose_name='FBM条码')),
                ('upc', models.CharField(blank=True, help_text='UPC', max_length=30, null=True, verbose_name='UPC')),
                ('item_id', models.CharField(blank=True, help_text='链接编号', max_length=30, null=True, verbose_name='链接编号')),
                ('image', models.ImageField(blank=True, help_text='产品图片', max_length=200, null=True, upload_to='ml_product', verbose_name='产品图片')),
                ('p_status', models.CharField(choices=[('NORMAL', '普通'), ('HOT_SALE', '热卖'), ('OFFLINE', '停售'), ('CLEAN', '清仓中')], default='ON_SALE', help_text='产品状态', max_length=10, verbose_name='产品状态')),
                ('qty', models.IntegerField(default=0, help_text='库存数量', verbose_name='库存数量')),
                ('onway_qty', models.IntegerField(default=0, help_text='在途数量', verbose_name='在途数量')),
                ('day15_sold', models.IntegerField(default=0, help_text='15天销量', verbose_name='15天销量')),
                ('day30_sold', models.IntegerField(default=0, help_text='30天销量', verbose_name='30天销量')),
                ('total_sold', models.IntegerField(default=0, help_text='累计销量', verbose_name='累计销量')),
                ('unit_cost', models.FloatField(blank=True, help_text='均摊成本价', null=True, verbose_name='均摊成本价')),
                ('first_ship_cost', models.FloatField(blank=True, help_text='均摊头程运费', null=True, verbose_name='均摊头程运费')),
                ('length', models.FloatField(blank=True, help_text='长cm', null=True, verbose_name='长cm')),
                ('width', models.FloatField(blank=True, help_text='宽cm', null=True, verbose_name='宽cm')),
                ('heigth', models.FloatField(blank=True, help_text='高cm', null=True, verbose_name='高cm')),
                ('weight', models.FloatField(blank=True, help_text='重量kg', null=True, verbose_name='重量kg')),
                ('total_profit', models.FloatField(blank=True, help_text='累计利润', null=True, verbose_name='累计利润')),
                ('total_weight', models.FloatField(blank=True, help_text='总重量kg', null=True, verbose_name='总重量kg')),
                ('total_cbm', models.FloatField(blank=True, help_text='总体积cbm', null=True, verbose_name='总体积cbm')),
                ('stock_value', models.FloatField(blank=True, help_text='库存价值rmb', null=True, verbose_name='库存价值rmb')),
                ('sale_url', models.CharField(blank=True, help_text='销售链接', max_length=500, null=True, verbose_name='销售链接')),
                ('note', models.TextField(blank=True, default='', help_text='备注', null=True, verbose_name='备注')),
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('is_active', models.BooleanField(default=True, help_text='是否启用', verbose_name='是否启用')),
                ('is_collect', models.BooleanField(default=True, help_text='是否收藏', verbose_name='是否收藏')),
                ('shop', models.ForeignKey(help_text='上架店铺', on_delete=django.db.models.deletion.CASCADE, related_name='shop_shopstock', to='mercado.shop', verbose_name='上架店铺')),
            ],
            options={
                'verbose_name': '店铺库存',
                'verbose_name_plural': '店铺库存',
                'ordering': ['-create_time'],
            },
        ),
    ]
