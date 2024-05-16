from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.shortcuts import redirect

import pyperclip

from .forms import OzonForm, Formating
from .models import Ozon
from utils.ozon.barcode_gen import barcode_gen, barcode_set
from utils.ozon.wwtk_2_windows import on_confirm, excel_edit, choice_file_xl
from utils.ozon import format_string as formating

SET_BARCODS = barcode_set


class XlFormCreateView(CreateView):
    model = Ozon
    form_class = OzonForm
    text = None

    def form_valid(self, form):
        if form.instance.barcode is None:
            barcode = barcode_gen(SET_BARCODS)
            form.instance.barcode = barcode
        if form.instance.article is None:
            form.instance.article = barcode
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET:
            if 'model_list_zipcom' in self.request.GET:
                self.text = formating.model_list_zipcom(
                    self.request.GET['text']
                )

        formater = Formating(initial={'text': self.text})
        context["form_formatter"] = formater
        return context


class XlFormDetailView(DetailView):
    model = Ozon


class XlFormUpdateView(UpdateView):
    model = Ozon
    form_class = OzonForm


class XlFormListView(ListView):
    model = Ozon
    ordering = '-id'
    paginate_by = 5


def edit_xl(request, pk):
    info = Ozon.objects.get(id=pk)
    on_confirm(
        info.title,
        info.article,
        info.barcode,
        info.annotacion,
        info.model_list,
        info.price,
        info.length,
        info.width,
        info.height,
        info.weight,
    )
    pyperclip.copy(info.barcode)
    excel_edit(choice_file_xl(info.xcel_shablon))
    return redirect('ozon:detail', pk=info.id)
