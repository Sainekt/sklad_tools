# Generated by Django 5.0.5 on 2024-05-08 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ozon', '0002_ozon_xcel_shablon'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ozon',
            name='barcode',
            field=models.CharField(max_length=255, null=True, verbose_name='Штрих-код'),
        ),
    ]
