# Generated by Django 3.2.4 on 2023-09-07 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0088_refillrecommend_advice'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipitemremove',
            name='handle',
            field=models.IntegerField(blank=True, default=0, help_text='处理结果', null=True, verbose_name='处理结果'),
        ),
        migrations.AddField(
            model_name='shipitemremove',
            name='handle_time',
            field=models.DateTimeField(blank=True, help_text='处理时间', null=True, verbose_name='处理时间'),
        ),
    ]
