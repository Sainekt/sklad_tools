from django import forms
from django.core.exceptions import ValidationError

from .models import Ozon


class OzonForm(forms.ModelForm):
    class Meta:
        model = Ozon
        fields = '__all__'
        widgets = {
            'annotacion': forms.Textarea({'cols': '22', 'rows': '5'}),
            'model_list': forms.Textarea({'cols': '22', 'rows': '5'}),
        }

    def clean_xcel_shablon(self):
        file = self.cleaned_data['xcel_shablon']
        if '.xlsx' not in file.name:
            raise ValidationError('Ожидается файл формата xlsx')
        return file


class FormatingForm(forms.Form):
    brand = forms.CharField(label='Брэнд', required=False)
    sep = forms.CharField(label='Разделитель', required=False)
    text = forms.CharField(label='Текст', widget=forms.Textarea(
        {'cols': '22', 'rows': '5'}), required=False,
        help_text='Будет помещено в основную таблицу при отправке данных.'
    )
