# Generated by Django 3.2.4 on 2023-02-15 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0068_purchasemanage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchasemanage',
            name='p_status',
            field=models.CharField(choices=[('WAITBUY', '待采购'), ('PURCHASED', '已采购'), ('RECEIVED', '已到货'), ('PACKED', '已打包'), ('USED', '已出库')], default='WAITBUY', help_text='采购单状态', max_length=10, verbose_name='采购单状态'),
        ),
    ]