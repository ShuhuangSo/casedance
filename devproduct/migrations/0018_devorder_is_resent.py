# Generated by Django 3.2.4 on 2024-09-13 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devproduct', '0017_auto_20240913_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='devorder',
            name='is_resent',
            field=models.BooleanField(default=False, help_text='是否重发订单', verbose_name='是否重发订单'),
        ),
    ]