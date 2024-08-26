from django.db import models


class Order(models.Model):
    name = models.CharField(max_length=100, verbose_name='Номер заказа')
    slug = models.SlugField(max_length=100, verbose_name='Слагифицирован')
    order_id = models.CharField(
        max_length=100, verbose_name='Api ID заказа', unique=True
    )
    created_at = models.DateField('Дата создания', auto_now_add=True)
    xl_doc = models.FileField(
        'Итоговый документ', blank=True, null=True, upload_to='purchaseorder'
    )


class Product(models.Model):
    product_id = models.SlugField(
        max_length=100, verbose_name='ID товара', unique=True
    )
    name = models.CharField(max_length=250, verbose_name='Наименование')
    code = models.CharField(
        max_length=100, verbose_name='Код товара', null=True, blank=True
    )
    article = models.CharField(
        max_length=100, verbose_name='Код товара', null=True, blank=True
    )
    barcodes = models.CharField(
        max_length=250, blank=True, null=True, verbose_name='Штрих-коды'
    )
    cell_number = models.CharField(
        verbose_name='Номер ячейки', max_length=100, null=True, blank=True
    )
    image = models.ImageField(
        verbose_name='Фото', blank=True, upload_to='purchaseorder', null=True)

    miniature = models.ImageField(
        verbose_name='фото миниатюра', blank=True, upload_to='purchaseorder',
        null=True
    )
    description = models.TextField('Описание', blank=True, null=True)


class PurchaseOrder(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='products'
    )
    quantity = models.IntegerField('Заказано шт')
    summ = models.FloatField('Сумма')
    fact = models.IntegerField('Фактическое количество', default=0)
    plus = models.IntegerField('Посчитано', null=True, blank=True)
    comment = models.CharField(
        'Комментарий', max_length=250, null=True, blank=True)
