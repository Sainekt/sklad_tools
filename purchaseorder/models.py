from django.db import models


class Order(models.Model):
    name = models.CharField(max_length=100, verbose_name='Номер заказа')
    created_at = models.DateField('Дата создания', auto_now_add=True)


class PurchaseOrder(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(
        verbose_name='Фото', blank=True, upload_to='purchaseorder', null=True)
    name = models.CharField('Название товара', max_length=250)
    code = models.CharField('Код товара', max_length=100)
    barcodes = models.CharField(
        'Баркоды', null=True, blank=True, max_length=250)
    quantity = models.IntegerField('Заказано шт')
    summ = models.FloatField('Сумма')
    fact = models.IntegerField('Фактическое количество', null=True, blank=True)
    comment = models.CharField(
        'Комментарий', max_length=250, null=True, blank=True)
