# Generated by Django 5.0.5 on 2024-05-14 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ozon', '0004_alter_ozon_barcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='ozon',
            name='weight',
            field=models.IntegerField(default=200, verbose_name='вес'),
        ),
    ]
