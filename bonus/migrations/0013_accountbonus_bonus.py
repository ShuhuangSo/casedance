# Generated by Django 3.2.4 on 2022-06-20 21:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bonus', '0012_auto_20220620_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountbonus',
            name='bonus',
            field=models.FloatField(blank=True, help_text='提成金额', null=True, verbose_name='提成金额'),
        ),
    ]