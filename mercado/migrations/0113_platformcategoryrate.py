# Generated by Django 3.2.4 on 2024-07-31 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0112_finance_note'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlatformCategoryRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(help_text='平台名称', max_length=10, verbose_name='平台名称')),
                ('site', models.CharField(help_text='站点名称', max_length=10, verbose_name='站点名称')),
                ('category_id', models.CharField(blank=True, help_text='类目id', max_length=30, null=True, verbose_name='类目id')),
                ('en_name', models.CharField(blank=True, help_text='英文类目名称', max_length=80, null=True, verbose_name='英文类目名称')),
                ('cn_name', models.CharField(blank=True, help_text='中文类目名称', max_length=80, null=True, verbose_name='中文类目名称')),
                ('first_category', models.CharField(blank=True, help_text='一级目录', max_length=80, null=True, verbose_name='一级目录')),
                ('fixed_fee0', models.FloatField(blank=True, help_text='固定费用(无店铺)', null=True, verbose_name='固定费用(无店铺)')),
                ('fixed_fee1', models.FloatField(blank=True, help_text='固定费用(有店铺)', null=True, verbose_name='固定费用(有店铺)')),
                ('fee0', models.FloatField(blank=True, help_text='无店铺佣金', null=True, verbose_name='无店铺佣金')),
                ('fee1', models.FloatField(blank=True, help_text='初级店铺佣金', null=True, verbose_name='初级店铺佣金')),
                ('fee2', models.FloatField(blank=True, help_text='中级店铺佣金', null=True, verbose_name='中级店铺佣金')),
                ('fee3', models.FloatField(blank=True, help_text='高级店铺佣金', null=True, verbose_name='高级店铺佣金')),
            ],
            options={
                'verbose_name': '平台类目佣金费率',
                'verbose_name_plural': '平台类目佣金费率',
            },
        ),
    ]