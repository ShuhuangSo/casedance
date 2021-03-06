# Generated by Django 3.2.4 on 2022-04-13 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0010_product_label_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='alert_days',
            field=models.IntegerField(blank=True, default=0, help_text='警戒天数', null=True, verbose_name='警戒天数'),
        ),
        migrations.AlterField(
            model_name='product',
            name='alert_qty',
            field=models.IntegerField(blank=True, default=0, help_text='警戒库存', null=True, verbose_name='警戒库存'),
        ),
        migrations.AlterField(
            model_name='product',
            name='max_pq',
            field=models.IntegerField(blank=True, default=0, help_text='采购上限', null=True, verbose_name='采购上限'),
        ),
        migrations.AlterField(
            model_name='product',
            name='mini_pq',
            field=models.IntegerField(blank=True, default=0, help_text='最小采购量', null=True, verbose_name='最小采购量'),
        ),
        migrations.AlterField(
            model_name='product',
            name='stock_days',
            field=models.IntegerField(blank=True, default=0, help_text='备货天数', null=True, verbose_name='备货天数'),
        ),
    ]
