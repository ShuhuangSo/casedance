# Generated by Django 3.2.4 on 2022-04-01 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0009_alter_supplier_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='label_name',
            field=models.CharField(blank=True, help_text='条码标签名', max_length=30, null=True, verbose_name='条码标签名'),
        ),
    ]
