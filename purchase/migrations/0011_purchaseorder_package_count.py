# Generated by Django 3.2.4 on 2022-04-20 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0010_auto_20220420_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseorder',
            name='package_count',
            field=models.IntegerField(default=0, help_text='发货箱数', verbose_name='发货箱数'),
        ),
    ]
