# Generated by Django 3.2.4 on 2022-06-16 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bonus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountsales',
            name='ad_percent',
            field=models.FloatField(blank=True, help_text='广告费占比', null=True, verbose_name='广告费占比'),
        ),
    ]