# Generated by Django 3.2.4 on 2022-12-17 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0061_ship_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='transstock',
            name='user_id',
            field=models.IntegerField(blank=True, default=0, help_text='创建人id', null=True, verbose_name='创建人id'),
        ),
    ]
