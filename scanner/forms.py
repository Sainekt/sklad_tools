from django import forms
# from django.core.exceptions import ValidationError

from .models import Scanner, MarketPlace


class ScannerForm(forms.ModelForm):
    class Meta:
        model = Scanner
        fields = '__all__'


class MarketForm(forms.ModelForm):
    class Meta:
        model = MarketPlace
        fields = '__all__'
