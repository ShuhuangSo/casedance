# Generated by Django 3.2.4 on 2022-07-28 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0013_alter_transapisetting_secretkey'),
    ]

    operations = [
        migrations.CreateModel(
            name='Keywords',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categ_id', models.CharField(help_text='类目id', max_length=10, verbose_name='类目id')),
                ('keyword', models.CharField(help_text='关键词', max_length=50, null=True, verbose_name='关键词')),
                ('t_keyword', models.CharField(help_text='关键词翻译', max_length=50, null=True, verbose_name='关键词翻译')),
                ('url', models.CharField(blank=True, help_text='url', max_length=200, null=True, verbose_name='url')),
                ('rank', models.IntegerField(blank=True, default=0, help_text='排名', null=True, verbose_name='排名')),
                ('status', models.CharField(help_text='状态', max_length=5, verbose_name='状态')),
                ('rank_changed', models.IntegerField(blank=True, default=0, help_text='排名变化', null=True, verbose_name='排名变化')),
                ('collection', models.BooleanField(default=False, help_text='是否收藏', verbose_name='是否收藏')),
                ('update_time', models.DateTimeField(auto_now_add=True, help_text='创建时间', verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '关键词',
                'verbose_name_plural': '关键词',
                'ordering': ['rank'],
            },
        ),
    ]