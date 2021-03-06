# Generated by Django 3.2.4 on 2022-04-01 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0007_alter_order_order_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='mode',
            field=models.CharField(choices=[('STANDARD', '标准流程'), ('POS', '快捷流程')], default='STANDARD', help_text='订单模式', max_length=10, verbose_name='订单模式'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('CANCEL', '作废'), ('PREPARING', '备货中'), ('READY', '已备货'), ('PART_SENT', '部分发货'), ('FINISHED', '已完成'), ('EXCEPTION', '异常')], default='PRE_SUMMIT', help_text='订单状态', max_length=20, verbose_name='订单状态'),
        ),
    ]
