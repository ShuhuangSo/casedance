# Generated by Django 3.2.4 on 2023-10-05 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0099_purchasemanage_platform'),
    ]

    operations = [
        migrations.AddField(
            model_name='refillsettings',
            name='platform',
            field=models.CharField(blank=True, help_text='平台', max_length=20, null=True, verbose_name='平台'),
        ),
    ]
