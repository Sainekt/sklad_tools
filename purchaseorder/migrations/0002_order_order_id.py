# Generated by Django 5.0.5 on 2024-08-08 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchaseorder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_id',
            field=models.CharField(default=1, max_length=100, verbose_name='Api ID заказа'),
            preserve_default=False,
        ),
    ]
