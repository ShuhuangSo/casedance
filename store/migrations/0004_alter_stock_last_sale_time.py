# Generated by Django 3.2.4 on 2022-03-29 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_stock_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='last_sale_time',
            field=models.DateTimeField(blank=True, help_text='最后一次销售时间', null=True, verbose_name='最后一次销售时间'),
        ),
    ]
