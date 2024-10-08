# Generated by Django 3.2.4 on 2024-09-02 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devproduct', '0009_alter_devproduct_online_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='devlistingaccount',
            name='is_paused',
            field=models.BooleanField(default=False, help_text='是否暂停', null=True, verbose_name='是否暂停'),
        ),
        migrations.AddField(
            model_name='devlistingaccount',
            name='notify',
            field=models.IntegerField(blank=True, default=0, help_text='通知标记', null=True, verbose_name='通知标记'),
        ),
    ]
