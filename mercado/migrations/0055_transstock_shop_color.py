# Generated by Django 3.2.4 on 2022-12-09 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0054_ship_shop_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='transstock',
            name='shop_color',
            field=models.CharField(blank=True, help_text='店铺颜色', max_length=30, null=True, verbose_name='店铺颜色'),
        ),
    ]