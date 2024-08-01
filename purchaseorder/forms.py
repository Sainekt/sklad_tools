from django.forms import ModelForm

from .models import PurchaseOrder


class ProductForm(ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ('plus', 'comment')


class FactForm(ProductForm):
    class Meta(ProductForm.Meta):
        fields = ('fact', 'comment')
