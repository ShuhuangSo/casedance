# Generated by Django 3.2.4 on 2022-11-20 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0027_alter_ship_book_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ship',
            name='book_date',
            field=models.DateField(blank=True, help_text='FBM预约日期', null=True, verbose_name='FBM预约日期'),
        ),
        migrations.AlterField(
            model_name='ship',
            name='end_date',
            field=models.DateField(blank=True, help_text='物流截单日期', null=True, verbose_name='物流截单日期'),
        ),
        migrations.AlterField(
            model_name='ship',
            name='ship_date',
            field=models.DateField(blank=True, help_text='航班日期', null=True, verbose_name='航班日期'),
        ),
    ]