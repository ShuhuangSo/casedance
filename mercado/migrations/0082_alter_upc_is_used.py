# Generated by Django 3.2.4 on 2023-03-12 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0081_upc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upc',
            name='is_used',
            field=models.BooleanField(default=False, help_text='是否使用', verbose_name='是否使用'),
        ),
    ]
