# Generated by Django 3.2.4 on 2022-04-16 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0009_delete_usermenu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='type',
            field=models.CharField(choices=[('PRODUCT', '产品标签'), ('ORDER', '订单标签'), ('PURCHASE', '采购标签'), ('CUSTOMER', '客户标签')], default='PRODUCT', help_text='标签类型', max_length=10, verbose_name='标签类型'),
        ),
    ]
