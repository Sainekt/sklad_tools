from django import forms

from .models import Ozon


class OzonForm(forms.ModelForm):
    class Meta:
        model = Ozon
        fields = '__all__'
        widgets = {
            'annotacion': forms.Textarea({'cols': '22', 'rows': '5'}),
            'model_list': forms.Textarea({'cols': '22', 'rows': '5'}),
        }


class Formating(forms.Form):
    brand = forms.CharField(label='Брэнд')
    sep = forms.CharField(label='Разделитель')
    text = forms.CharField(label='Текст', widget=forms.Textarea(
        {'cols': '22', 'rows': '5'}), required=False,
    )
