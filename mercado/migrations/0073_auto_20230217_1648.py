# Generated by Django 3.2.4 on 2023-02-17 16:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0072_purchasemanage_pack_qty'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchasemanage',
            name='is_renew',
        ),
        migrations.RemoveField(
            model_name='purchasemanage',
            name='need_qty',
        ),
    ]
