# Generated by Django 3.2.4 on 2022-11-18 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0022_shop_shopstock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='shop_type',
            field=models.CharField(blank=True, help_text='店铺类型', max_length=30, null=True, verbose_name='店铺类型'),
        ),
    ]
