# Generated by Django 3.2.4 on 2023-03-21 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0085_auto_20230321_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopstock',
            name='day7_sold',
            field=models.IntegerField(default=0, help_text='7天销量', verbose_name='7天销量'),
        ),
    ]
