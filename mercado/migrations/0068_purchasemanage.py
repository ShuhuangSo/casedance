# Generated by Django 3.2.4 on 2023-02-15 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0067_shipdetail_plan_qty'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseManage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('p_status', models.CharField(help_text='采购单状态', max_length=10, verbose_name='采购单状态')),
                ('s_type', models.CharField(help_text='货品类型', max_length=10, verbose_name='货品类型')),
                ('create_type', models.CharField(help_text='创建方式', max_length=10, verbose_name='创建方式')),
                ('sku', models.CharField(help_text='产品SKU', max_length=30, verbose_name='产品SKU')),
                ('p_name', models.CharField(help_text='产品名称', max_length=80, verbose_name='产品名称')),
                ('label_code', models.CharField(blank=True, help_text='FBM条码', max_length=30, null=True, verbose_name='FBM条码')),
                ('item_id', models.CharField(blank=True, help_text='链接编号', max_length=30, null=True, verbose_name='链接编号')),
                ('image', models.ImageField(blank=True, help_text='产品图片', max_length=200, null=True, upload_to='ml_product', verbose_name='产品图片')),
                ('unit_cost', models.FloatField(default=0, help_text='成本价', null=True, verbose_name='成本价')),
                ('length', models.FloatField(blank=True, help_text='长cm', null=True, verbose_name='长cm')),
                ('width', models.FloatField(blank=True, help_text='宽cm', null=True, verbose_name='宽cm')),
                ('heigth', models.FloatField(blank=True, help_text='高cm', null=True, verbose_name='高cm')),
                ('weight', models.FloatField(blank=True, help_text='重量kg', null=True, verbose_name='重量kg')),
                ('need_qty', models.IntegerField(default=0, help_text='需求数量', verbose_name='需求数量')),
                ('buy_qty', models.IntegerField(default=0, help_text='采购数量', verbose_name='采购数量')),
                ('rec_qty', models.IntegerField(default=0, help_text='收货数量', verbose_name='收货数量')),
                ('used_qty', models.IntegerField(default=0, help_text='出库数量', verbose_name='出库数量')),
                ('used_batch', models.CharField(help_text='使用批次', max_length=30, verbose_name='使用批次')),
                ('note', models.CharField(blank=True, help_text='短备注', max_length=300, null=True, verbose_name='短备注')),
                ('shop', models.CharField(blank=True, help_text='目标店铺', max_length=30, null=True, verbose_name='目标店铺')),
                ('shop_color', models.CharField(blank=True, help_text='店铺颜色', max_length=20, null=True, verbose_name='店铺颜色')),
                ('packing_name', models.CharField(blank=True, help_text='包材名称', max_length=80, null=True, verbose_name='包材名称')),
                ('packing_size', models.CharField(blank=True, help_text='包材尺寸', max_length=80, null=True, verbose_name='包材尺寸')),
                ('create_time', models.DateTimeField(blank=True, help_text='创建时间', null=True, verbose_name='创建时间')),
                ('buy_time', models.DateTimeField(blank=True, help_text='采购时间', null=True, verbose_name='采购时间')),
                ('rec_time', models.DateTimeField(blank=True, help_text='到货时间', null=True, verbose_name='到货时间')),
                ('pack_time', models.DateTimeField(blank=True, help_text='打包时间', null=True, verbose_name='打包时间')),
                ('used_time', models.DateTimeField(blank=True, help_text='出库时间', null=True, verbose_name='出库时间')),
                ('location', models.CharField(blank=True, help_text='仓位', max_length=30, null=True, verbose_name='仓位')),
                ('is_renew', models.BooleanField(default=False, help_text='是否更新', verbose_name='是否更新')),
                ('is_urgent', models.BooleanField(default=False, help_text='是否紧急', verbose_name='是否紧急')),
            ],
            options={
                'verbose_name': '采购管理',
                'verbose_name_plural': '采购管理',
                'ordering': ['-create_time'],
            },
        ),
    ]
