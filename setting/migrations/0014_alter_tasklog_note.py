# Generated by Django 3.2.4 on 2022-08-01 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0013_sysrefill'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasklog',
            name='note',
            field=models.CharField(help_text='任务注释', max_length=20, verbose_name='任务注释'),
        ),
    ]
