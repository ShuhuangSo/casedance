# Generated by Django 3.2.4 on 2023-01-17 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0065_shopreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopreport',
            name='profit',
            field=models.FloatField(default=0.0, help_text='利润rmb', verbose_name='利润rmb'),
        ),
    ]
