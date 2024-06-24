# from django.shortcuts import render
from django.views import generic

from .models import Scanner, MarketPlace
from .forms import ScannerForm, MarketForm


class ScannerPage(generic.TemplateView):
    template_name = 'scanner/main.html'


class ScannerCreate(generic.CreateView):
    model = Scanner
    form_class = ScannerForm


class MarketPlaceCreate(generic.CreateView):
    model = MarketPlace
    form_class = MarketForm
    template_name = 'scanner/market_form.html'
