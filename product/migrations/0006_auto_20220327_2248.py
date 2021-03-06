# Generated by Django 3.2.4 on 2022-03-27 22:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0005_compatiblemodel'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='compatiblemodel',
            options={'ordering': ['phone_model'], 'verbose_name': '产品兼容手机型号', 'verbose_name_plural': '产品兼容手机型号'},
        ),
        migrations.AlterModelOptions(
            name='devicemodel',
            options={'ordering': ['model'], 'verbose_name': '市面手机型号表', 'verbose_name_plural': '市面手机型号表'},
        ),
        migrations.AlterField(
            model_name='compatiblemodel',
            name='phone_model',
            field=models.ForeignKey(help_text='市面手机型号', on_delete=django.db.models.deletion.DO_NOTHING, related_name='device_comp_model', to='product.devicemodel', verbose_name='市面手机型号'),
        ),
        migrations.AlterField(
            model_name='compatiblemodel',
            name='product',
            field=models.ForeignKey(help_text='产品', on_delete=django.db.models.deletion.DO_NOTHING, related_name='product_comp_model', to='product.product', verbose_name='产品'),
        ),
    ]
