from django.views.generic import CreateView, DetailView

from .forms import OzonForm
from .models import Ozon


class XlFormCreateView(CreateView):
    model = Ozon
    form_class = OzonForm


class XlFormDetailView(DetailView):
    model = Ozon
