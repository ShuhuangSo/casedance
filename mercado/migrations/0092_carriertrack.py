# Generated by Django 3.2.4 on 2023-09-21 16:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0091_auto_20230908_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='CarrierTrack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('carrier_name', models.CharField(blank=True, help_text='物流商名称', max_length=30, null=True, verbose_name='物流商名称')),
                ('carrier_number', models.CharField(blank=True, help_text='物流商单号', max_length=30, null=True, verbose_name='物流商单号')),
                ('context', models.CharField(blank=True, help_text='节点描述', max_length=100, null=True, verbose_name='节点描述')),
                ('location', models.CharField(blank=True, help_text='位置', max_length=30, null=True, verbose_name='位置')),
                ('status', models.CharField(blank=True, help_text='状态', max_length=30, null=True, verbose_name='状态')),
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
                ('time', models.DateTimeField(blank=True, help_text='时间', null=True, verbose_name='时间')),
                ('optime', models.DateTimeField(blank=True, help_text='操作时间', null=True, verbose_name='操作时间')),
                ('ship', models.ForeignKey(help_text='所属运单', on_delete=django.db.models.deletion.CASCADE, related_name='ship_tracking', to='mercado.ship', verbose_name='所属运单')),
            ],
            options={
                'verbose_name': '物流跟踪',
                'verbose_name_plural': '物流跟踪',
                'ordering': ['create_time'],
            },
        ),
    ]