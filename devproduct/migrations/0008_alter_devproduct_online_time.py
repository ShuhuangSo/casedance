# Generated by Django 3.2.4 on 2024-08-29 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devproduct', '0007_devproduct_online_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devproduct',
            name='online_time',
            field=models.DateTimeField(blank=True, help_text='发布的时间', null=True, verbose_name='发布的时间'),
        ),
    ]