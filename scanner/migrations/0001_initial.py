# Generated by Django 5.0.5 on 2024-06-02 10:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MarketPlace',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('market', models.CharField(max_length=255, verbose_name='Название маркетплейса')),
            ],
            options={
                'verbose_name': 'маркетплейс',
                'verbose_name_plural': 'Маркетплейсы',
            },
        ),
        migrations.CreateModel(
            name='Scanner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('barcode', models.CharField(max_length=255, verbose_name='Идентификатор заказа')),
                ('scan_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время сканирования')),
                ('market', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='scanner.marketplace', verbose_name='Маркетплейс')),
            ],
        ),
    ]
