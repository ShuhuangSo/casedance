# Generated by Django 3.2.4 on 2022-12-09 16:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0056_remove_transstock_shop_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ship',
            name='shop_color',
        ),
    ]
