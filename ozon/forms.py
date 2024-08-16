from django import forms
from django.core.exceptions import ValidationError
from .utils import ParserTree

from .models import Ozon


class OzonForm(forms.ModelForm):
    class Meta:
        model = Ozon
        fields = '__all__'
        widgets = {
            'annotacion': forms.Textarea({'cols': '22', 'rows': '5'}),
            'model_list': forms.Textarea({'cols': '22', 'rows': '5'}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'xcel_shablon': forms.ClearableFileInput(
                attrs={'accept': '.xlsx'}),
        }

    def clean_xcel_shablon(self):
        file = self.cleaned_data['xcel_shablon']
        if '.xlsx' not in file.name:
            raise ValidationError('Ожидается файл формата xlsx')
        return file

    def clean_image(self):
        image_formats = [
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp'
        ]
        file = self.cleaned_data.get('image')
        if file:
            if file.name.split('.')[-1] not in image_formats:
                raise ValidationError('Ожидается изображение.')
            return file


class FormatingForm(forms.Form):
    brand = forms.CharField(label='Брэнд', required=False)
    sep = forms.CharField(label='Разделитель', required=False)
    text = forms.CharField(label='Текст', widget=forms.Textarea(
        {'cols': '22', 'rows': '5'}), required=False,
        help_text='Будет помещено в основную таблицу при отправке данных.'
    )

class SearchForm(forms.Form):
    cat_search = forms.CharField(required=False)
