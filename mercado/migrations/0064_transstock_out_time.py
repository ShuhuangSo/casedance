# Generated by Django 3.2.4 on 2023-01-09 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0063_mlproduct_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='transstock',
            name='out_time',
            field=models.DateTimeField(blank=True, help_text='出仓时间', null=True, verbose_name='出仓时间'),
        ),
    ]