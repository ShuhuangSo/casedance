# Generated by Django 3.2.4 on 2022-11-21 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0030_alter_carrier_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipbox',
            name='carrier_box_number',
            field=models.CharField(blank=True, help_text='物流商箱唛号', max_length=30, null=True, verbose_name='物流商箱唛号'),
        ),
    ]
