# Generated by Django 3.2.4 on 2022-03-31 12:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0005_auto_20220331_1139'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseorder',
            name='total_cost',
        ),
        migrations.RemoveField(
            model_name='purchaseorder',
            name='total_paid',
        ),
    ]