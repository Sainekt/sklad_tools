from django.db import models
from django.urls import reverse

from sklad_tools import settings


class MarketPlace(models.Model):
    """Название маркетплейса к котрому относится идентификатор"""

    market = models.CharField(
        verbose_name='Название маркетплейса',
        max_length=settings.DEFAULT_CHAR_LENGTH
    )

    def __str__(self):
        return self.market

    class Meta:
        verbose_name = 'маркетплейс'
        verbose_name_plural = 'Маркетплейсы'

    def get_absolute_url(self):
        return reverse('scanner:main')


class Scanner(models.Model):
    """Модель просканированных идентификаторов."""

    barcode = models.CharField(
        verbose_name='Идентификатор заказа',
        max_length=settings.DEFAULT_CHAR_LENGTH,
    )
    scan_date = models.DateTimeField(
        verbose_name='Дата и время сканирования',
        auto_now_add=True
    )

    market = models.ForeignKey(
        MarketPlace,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Маркетплейс'
    )

    def __str__(self):
        return self.barcode
    
    def get_absolute_url(self):
        return reverse('scanner:pik')
    

    class Meta:
        default_related_name = 'barcods'
        verbose_name = 'штрих-код'
        verbose_name_plural = 'Штрих-коды'
        ordering = ('-scan_date',)
