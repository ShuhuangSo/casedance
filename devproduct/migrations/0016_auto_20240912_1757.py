# Generated by Django 3.2.4 on 2024-09-12 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devproduct', '0015_devprice_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='devprice',
            name='brand',
            field=models.CharField(blank=True, help_text='品牌', max_length=20, null=True, verbose_name='品牌'),
        ),
        migrations.AddField(
            model_name='devprice',
            name='cn_material',
            field=models.CharField(blank=True, help_text='中文材质', max_length=30, null=True, verbose_name='中文材质'),
        ),
        migrations.AddField(
            model_name='devprice',
            name='custom_cn_name',
            field=models.CharField(blank=True, help_text='申报中文品名', max_length=30, null=True, verbose_name='申报中文品名'),
        ),
        migrations.AddField(
            model_name='devprice',
            name='custom_code',
            field=models.CharField(blank=True, help_text='海关编码', max_length=20, null=True, verbose_name='海关编码'),
        ),
        migrations.AddField(
            model_name='devprice',
            name='custom_en_name',
            field=models.CharField(blank=True, help_text='申报英文品名', max_length=30, null=True, verbose_name='申报英文品名'),
        ),
        migrations.AddField(
            model_name='devprice',
            name='declared_value',
            field=models.FloatField(blank=True, help_text='申报价值USD', max_length=30, null=True, verbose_name='申报价值USD'),
        ),
        migrations.AddField(
            model_name='devprice',
            name='en_material',
            field=models.CharField(blank=True, help_text='英文材质', max_length=30, null=True, verbose_name='英文材质'),
        ),
        migrations.AddField(
            model_name='devprice',
            name='upc',
            field=models.CharField(blank=True, help_text='UPC', max_length=30, null=True, verbose_name='UPC'),
        ),
        migrations.AddField(
            model_name='devprice',
            name='use',
            field=models.CharField(blank=True, help_text='用途', max_length=50, null=True, verbose_name='用途'),
        ),
    ]