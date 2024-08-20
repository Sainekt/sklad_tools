from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import PurchaseOrder


class ProductForm(ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ('plus', 'comment')


class FactForm(ProductForm):
    class Meta(ProductForm.Meta):
        fields = ('fact', 'comment')

    def clean_fact(self):
        data = self.cleaned_data['fact']
        if data < 0:
            raise ValidationError('Чисто не может быть отрицательным')
        return data
