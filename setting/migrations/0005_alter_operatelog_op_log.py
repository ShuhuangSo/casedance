# Generated by Django 3.2.4 on 2022-03-29 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0004_operatelog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='operatelog',
            name='op_log',
            field=models.TextField(blank=True, default='', help_text='操作描述', null=True, verbose_name='操作描述'),
        ),
    ]
