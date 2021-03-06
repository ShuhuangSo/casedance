# Generated by Django 3.2.4 on 2022-06-20 22:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bonus', '0013_accountbonus_bonus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountbonus',
            name='manager',
            field=models.ForeignKey(help_text='账号负责人', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='manager_bonus', to='bonus.manager', verbose_name='账号负责人'),
        ),
    ]
