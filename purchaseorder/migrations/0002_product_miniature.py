# Generated by Django 5.0.5 on 2024-08-20 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchaseorder', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='miniature',
            field=models.ImageField(blank=True, null=True, upload_to='purchaseorder', verbose_name='фото миниатюра'),
        ),
    ]
