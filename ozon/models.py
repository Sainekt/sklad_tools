from django.db import models
from django.urls import reverse

from sklad_tools import settings

annotacion_text = (
    """Совместимость с брендом: 
Материал: 
Цвет: """
)


class Ozon(models.Model):
    title = models.CharField(
        'Наименование', max_length=settings.DEFAULT_CHAR_LENGTH)
    article = models.CharField(
        'Артикул', max_length=settings.DEFAULT_CHAR_LENGTH,
        null=True, blank=True,
    )
    barcode = models.CharField(
        'Штрих-код', max_length=settings.DEFAULT_CHAR_LENGTH,
        null=True, blank=True
    )
    price = models.IntegerField('Цена руб.', default=10000)
    length = models.IntegerField('Длина упаковки мм.', default=180)
    width = models.IntegerField('Ширина упаковки мм.', default=120)
    height = models.IntegerField('Высота упаковки мм.', default=100)
    weight = models.IntegerField('вес', default=200)
    annotacion = models.TextField(
        'Аннотация', max_length=5000, default=annotacion_text)
    model_list = models.TextField(
        'Список совместимых устройств', max_length=5000
    )
    xcel_shablon = models.FileField('XL шаблон', upload_to='ozon_shablons')
    image = models.FileField(
        "Фото", upload_to='foto', null=True, blank=True
    )

    def get_absolute_url(self):
        return reverse("ozon:edit_xl", kwargs={"pk": self.pk})
