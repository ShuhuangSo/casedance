# Generated by Django 3.2.4 on 2023-03-22 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0086_shopstock_day7_sold'),
    ]

    operations = [
        migrations.AddField(
            model_name='refillrecommend',
            name='image',
            field=models.ImageField(blank=True, help_text='产品图片', max_length=200, null=True, upload_to='ml_product', verbose_name='产品图片'),
        ),
    ]
