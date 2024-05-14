from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.shortcuts import redirect

import pyperclip

from .forms import OzonForm
from .models import Ozon
from utils.ozon.barcode_gen import barcode_gen, barcode_set
from utils.ozon.wwtk_2_windows import on_confirm, excel_edit, choice_file_xl

SET_BARCODS = barcode_set


class XlFormCreateView(CreateView):
    model = Ozon
    form_class = OzonForm

    def form_valid(self, form):
        if form.instance.barcode is None:
            form.instance.barcode = barcode_gen(SET_BARCODS)
        # choice_file_xl(form.instance.xcel_shablon)
        return super().form_valid(form)


class XlFormDetailView(DetailView):
    model = Ozon


class XlFormUpdateView(UpdateView):
    model = Ozon
    form_class = OzonForm


class XlFormListView(ListView):
    model = Ozon
    ordering = '-id'
    paginate_by = 10


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
