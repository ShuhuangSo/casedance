# Generated by Django 3.2.4 on 2022-03-31 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0004_alter_purchaseorder_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasedetail',
            name='is_supply_case',
            field=models.BooleanField(default=False, help_text='是否提供素材壳', verbose_name='是否提供素材壳'),
        ),
        migrations.AddField(
            model_name='purchasedetail',
            name='sent_qty',
            field=models.IntegerField(default=0, help_text='发货数量', verbose_name='发货数量'),
        ),
        migrations.AlterField(
            model_name='purchaseorder',
            name='order_status',
            field=models.CharField(choices=[('CANCEL', '作废'), ('PRE_SUMMIT', '未提交'), ('WAIT_CONFIRM', '待确认'), ('IN_PRODUCTION', '生产中'), ('SENT', '已发货'), ('PART_SENT', '部分发货'), ('PART_REC', '部分收货'), ('FINISHED', '已完成'), ('EXCEPTION', '异常')], default='PRE_SUMMIT', help_text='采购单状态', max_length=20, verbose_name='采购单状态'),
        ),
    ]
