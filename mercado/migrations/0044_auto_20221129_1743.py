# Generated by Django 3.2.4 on 2022-11-29 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0043_remove_shop_currency'),
    ]

    operations = [
        migrations.AddField(
            model_name='mlorder',
            name='currency',
            field=models.CharField(blank=True, help_text='币种', max_length=5, null=True, verbose_name='币种'),
        ),
        migrations.AddField(
            model_name='shop',
            name='currency',
            field=models.CharField(blank=True, help_text='币种', max_length=10, null=True, verbose_name='币种'),
        ),
    ]