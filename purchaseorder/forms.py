from django.forms import ModelForm
from django import forms
from django.core.exceptions import ValidationError
from .models import PurchaseOrder, Product


class ProductForm(ModelForm):
    plus = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}))
    comment = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=250
    )

    class Meta:
        model = PurchaseOrder
        fields = ('plus', 'comment')


class FactForm(ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ('fact', 'comment')

    def clean_fact(self):
        data = self.cleaned_data['fact']
        if data < 0:
            raise ValidationError('Чисто не может быть отрицательным')
        return data


class DetailLabelForm(ModelForm):
    date = forms.DateField(
        label='Дата приемки',
        widget=forms.DateInput(attrs={'type': 'date'}))
    big = forms.BooleanField(label='Большая', required=False)

    class Meta:
        model = Product
        fields = ('name', 'code', 'barcodes', 'cell_number')
