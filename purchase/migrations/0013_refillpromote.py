# Generated by Django 3.2.4 on 2022-05-12 13:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_auto_20220503_2309'),
        ('purchase', '0012_auto_20220420_2316'),
    ]

    operations = [
        migrations.CreateModel(
            name='RefillPromote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qty', models.IntegerField(default=0, help_text='推荐采购数量', verbose_name='推荐采购数量')),
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('product', models.ForeignKey(help_text='产品', on_delete=django.db.models.deletion.CASCADE, related_name='product_Refill', to='product.product', verbose_name='产品')),
            ],
            options={
                'verbose_name': '智能补货推荐',
                'verbose_name_plural': '智能补货推荐',
                'ordering': ['create_time'],
            },
        ),
    ]