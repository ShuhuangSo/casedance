# Generated by Django 3.2.4 on 2023-10-09 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0102_mlorder_exc_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mlorder',
            name='exc_currency',
            field=models.CharField(blank=True, help_text='结算币种', max_length=5, null=True, verbose_name='结算币种'),
        ),
    ]
