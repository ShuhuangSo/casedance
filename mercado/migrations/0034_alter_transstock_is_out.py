# Generated by Django 3.2.4 on 2022-11-24 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0033_transstock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transstock',
            name='is_out',
            field=models.BooleanField(default=False, help_text='是否已出仓', verbose_name='是否已出仓'),
        ),
    ]
