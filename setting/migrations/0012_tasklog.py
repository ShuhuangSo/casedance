# Generated by Django 3.2.4 on 2022-05-12 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0011_alter_tag_tag_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_type', models.IntegerField(default=0, help_text='任务类型', verbose_name='任务类型')),
                ('note', models.CharField(help_text='任务注释', max_length=10, verbose_name='任务注释')),
                ('create_time', models.DateTimeField(auto_now_add=True, help_text='执行时间', verbose_name='执行时间')),
            ],
            options={
                'verbose_name': '任务执行日志',
                'verbose_name_plural': '任务执行日志',
                'ordering': ['-create_time'],
            },
        ),
    ]