# Generated by Django 3.2.4 on 2024-09-12 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devproduct', '0014_devproduct_local_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='devprice',
            name='note',
            field=models.TextField(blank=True, default='', help_text='备注', null=True, verbose_name='备注'),
        ),
    ]