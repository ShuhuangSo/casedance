# Generated by Django 3.2.4 on 2022-07-12 15:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0003_alter_listing_currency'),
    ]

    operations = [
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seller_id', models.CharField(help_text='卖家id', max_length=10, verbose_name='卖家id')),
                ('site_id', models.CharField(help_text='站点id', max_length=10, verbose_name='站点id')),
                ('nickname', models.CharField(help_text='卖家名称', max_length=30, verbose_name='卖家名称')),
                ('level_id', models.CharField(help_text='信誉水平', max_length=30, verbose_name='信誉水平')),
                ('total', models.IntegerField(blank=True, default=0, help_text='总订单', null=True, verbose_name='总订单')),
                ('canceled', models.IntegerField(blank=True, default=0, help_text='取消订单', null=True, verbose_name='取消订单')),
                ('negative', models.FloatField(blank=True, help_text='差评率', null=True, verbose_name='差评率')),
                ('neutral', models.FloatField(blank=True, help_text='中评率', null=True, verbose_name='中评率')),
                ('positive', models.FloatField(blank=True, help_text='好评率', null=True, verbose_name='好评率')),
                ('registration_date', models.DateTimeField(help_text='注册时间', null=True, verbose_name='注册时间')),
            ],
            options={
                'verbose_name': '卖家',
                'verbose_name_plural': '卖家',
                'ordering': ['-registration_date'],
            },
        ),
    ]