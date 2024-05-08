from django.views.generic import CreateView, DetailView, UpdateView, ListView

from .forms import OzonForm
from .models import Ozon
from utils.ozon.barcode_gen import barcode_gen, barcode_set

SET_BARCODS = barcode_set


class XlFormCreateView(CreateView):
    model = Ozon
    form_class = OzonForm

    def form_valid(self, form):
        if form.instance.barcode is None:
            form.instance.barcode = barcode_gen(SET_BARCODS)
        return super().form_valid(form)


class XlFormDetailView(DetailView):
    model = Ozon


class XlFormUpdateView(UpdateView):
    model = Ozon
    form_class = OzonForm


class XlFormListView(ListView):
    model = Ozon
    ordering = '-id'

