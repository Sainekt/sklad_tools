# Generated by Django 5.0.5 on 2024-07-31 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ozon', '0008_ozon_image_alter_ozon_annotacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ozon',
            name='annotacion',
            field=models.TextField(default='Совместимость с брендом: \nМатериал: \nЦвет: ', max_length=5000, verbose_name='Аннотация'),
        ),
    ]
