# Generated by Django 3.2.4 on 2022-07-25 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado', '0008_categories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categories',
            name='father_id',
            field=models.CharField(help_text='父类目id', max_length=10, null=True, verbose_name='父类目id'),
        ),
        migrations.AlterField(
            model_name='categories',
            name='name',
            field=models.CharField(help_text='类目名称', max_length=100, null=True, verbose_name='类目名称'),
        ),
        migrations.AlterField(
            model_name='categories',
            name='t_name',
            field=models.CharField(help_text='翻译类目名称', max_length=100, null=True, verbose_name='翻译类目名称'),
        ),
    ]