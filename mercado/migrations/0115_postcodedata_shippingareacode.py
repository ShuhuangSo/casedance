# Generated by Django 3.2.4 on 2024-09-07 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0114_shippingprice'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostCodeData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(help_text='国家', max_length=10, verbose_name='国家')),
                ('postcode', models.CharField(help_text='邮编', max_length=10, verbose_name='邮编')),
                ('suburb', models.CharField(blank=True, help_text='城市区域', max_length=80, null=True, verbose_name='城市区域')),
                ('state_code', models.CharField(blank=True, help_text='州', max_length=20, null=True, verbose_name='州')),
            ],
            options={
                'verbose_name': '邮编字典',
                'verbose_name_plural': '邮编字典',
            },
        ),
        migrations.CreateModel(
            name='ShippingAreaCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(help_text='国家', max_length=10, verbose_name='国家')),
                ('carrier_name', models.CharField(blank=True, help_text='物流名称', max_length=50, null=True, verbose_name='物流名称')),
                ('carrier_code', models.CharField(blank=True, help_text='物流代码', max_length=30, null=True, verbose_name='物流代码')),
                ('postcode', models.CharField(help_text='邮编', max_length=10, verbose_name='邮编')),
                ('area', models.CharField(blank=True, help_text='分区', max_length=30, null=True, verbose_name='分区')),
                ('is_avaiable', models.BooleanField(default=True, help_text='配送服务', verbose_name='配送服务')),
                ('note', models.CharField(blank=True, help_text='简要备注', max_length=100, null=True, verbose_name='简要备注')),
                ('update_time', models.DateTimeField(blank=True, help_text='更新时间', null=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '物流服务分区',
                'verbose_name_plural': '物流服务分区',
            },
        ),
    ]