# Generated by Django 3.2.4 on 2022-06-16 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bonus', '0007_accountsales_ad_fees_rmb'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accounts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(blank=True, default=0, help_text='帐号类型', null=True, verbose_name='帐号类型')),
                ('name', models.CharField(blank=True, help_text='帐号名称', max_length=30, null=True, verbose_name='帐号名称')),
                ('note', models.CharField(blank=True, help_text='备注', max_length=100, null=True, verbose_name='备注')),
            ],
            options={
                'verbose_name': '帐号',
                'verbose_name_plural': '帐号',
                'ordering': ['-name'],
            },
        ),
    ]
