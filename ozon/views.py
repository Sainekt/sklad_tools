from django.views.generic import CreateView, DetailView, UpdateView, ListView

from .forms import OzonForm
from .models import Ozon


class XlFormCreateView(CreateView):
    model = Ozon
    form_class = OzonForm


class XlFormDetailView(DetailView):
    model = Ozon


class XlFormUpdateView(UpdateView):
    model = Ozon
    form_class = OzonForm


class XlFormListView(ListView):
    model = Ozon
    ordering = '-id'

