from typing import Any
from django.views.generic import CreateView, DetailView, UpdateView, ListView, FormView
from django.shortcuts import redirect, render

import pyperclip

from .forms import OzonForm, FormatingForm
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
        print(form.instance.title)
        if form.instance.barcode is None:
            barcode = barcode_gen(SET_BARCODS)
            form.instance.barcode = barcode
        if form.instance.article is None:
            form.instance.article = barcode
        if form.instance.model_list is None and self.text:
            form.instance.model_list = self.text
        return super().form_valid(form)


class XlFormDetailView(DetailView):
    model = Ozon


class XlFormUpdateView(UpdateView):
    model = Ozon
    form_class = OzonForm
    text = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.GET:
            if 'model_list_zipcom' in self.request.GET:
                self.text = formating.model_list_zipcom(
                    self.request.GET['text']
                )
        formater = FormatingForm(initial={'text': self.text})
        context["form_formatter"] = formater
        return context


class XlFormListView(ListView):
    model = Ozon
    ordering = '-id'
    paginate_by = 5


class Formatter(FormView):
    template_name = 'blog/detail.html'
    form_class = FormatingForm
    text = None
    def form_valid(self, form):
        form
        return super().form_valid(form)
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.brand, self.sep = formating.get_Separation()
        if self.request.POST:
            self.text = get_format_strgin(
                number=self.request.POST['button'],
                text=self.request.POST['text'],
                brand=self.request.POST['brand'],
                sep=self.request.POST['sep']
            )
        form = FormatingForm(
            initial={
                'text': self.text,
                'brand': self.brand,
                'sep': self.sep}
        )
        context["form"] = form
        return context



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


def get_format_strgin(number, text, brand=None, sep=None):
    funcs = {
        '1': formating.brands_by_sep,
        '2': formating.model_list_zipcom,
        '3': formating.del_enter,
        '4': formating.del_brand,
        '5': formating.model_list_doc_cm,
        '6': formating.fiyo,
    }
    if number == '1':
        return funcs[number](brand=brand, separation=sep, text=text)
    return funcs[number](text)
