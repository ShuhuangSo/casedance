# Generated by Django 3.2.4 on 2022-06-18 11:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bonus', '0009_monthlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='accounts',
            name='manager',
            field=models.ForeignKey(help_text='账号负责人', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='manager_accounts', to='bonus.manager', verbose_name='账号负责人'),
        ),
        migrations.AlterField(
            model_name='accounts',
            name='type',
            field=models.CharField(blank=True, help_text='平台', max_length=30, null=True, verbose_name='平台'),
        ),
    ]