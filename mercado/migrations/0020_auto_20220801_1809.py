# Generated by Django 3.2.4 on 2022-08-01 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0019_sellertrack'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='seller',
            options={'ordering': ['-id'], 'verbose_name': '卖家', 'verbose_name_plural': '卖家'},
        ),
        migrations.AddField(
            model_name='seller',
            name='note',
            field=models.TextField(blank=True, default='', help_text='备注', null=True, verbose_name='备注'),
        ),
    ]