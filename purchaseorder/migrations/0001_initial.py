# Generated by Django 5.0.5 on 2024-08-06 13:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Номер заказа')),
                ('slug', models.SlugField(max_length=100, verbose_name='Слагифицирован')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Дата создания')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.SlugField(max_length=100, verbose_name='ID товара')),
                ('name', models.CharField(max_length=250, verbose_name='Наименование')),
                ('code', models.CharField(blank=True, max_length=100, null=True, verbose_name='Код товара')),
                ('article', models.CharField(blank=True, max_length=100, null=True, verbose_name='Код товара')),
                ('barcodes', models.CharField(blank=True, max_length=250, null=True, verbose_name='Штрих-коды')),
                ('cell_number', models.CharField(blank=True, max_length=100, null=True, verbose_name='Номер ячейки')),
                ('image', models.ImageField(blank=True, null=True, upload_to='purchaseorder', verbose_name='Фото')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(verbose_name='Заказано шт')),
                ('summ', models.FloatField(verbose_name='Сумма')),
                ('fact', models.IntegerField(default=0, verbose_name='Фактическое количество')),
                ('plus', models.IntegerField(blank=True, null=True, verbose_name='Посчитано')),
                ('comment', models.CharField(blank=True, max_length=250, null=True, verbose_name='Комментарий')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='purchaseorder.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='purchaseorder.product')),
            ],
        ),
    ]
