# Generated by Django 3.2.4 on 2022-04-03 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_alter_stocklog_op_log'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stocklog',
            name='op_log',
        ),
        migrations.AddField(
            model_name='stocklog',
            name='op_origin_id',
            field=models.IntegerField(blank=True, help_text='操作单id', null=True, verbose_name='操作单id'),
        ),
    ]
