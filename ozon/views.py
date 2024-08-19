from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.shortcuts import redirect, render
from django.views import View
from django import forms
import ast

from .forms import OzonForm, FormatingForm, SearchForm
from .models import Ozon
from utils.ozon.barcode_gen import barcode_gen, barcode_set
from utils.ozon.writer_ozon_form import (
    on_confirm, excel_edit, choice_file_xl, clean_shablon_dir
)
from utils.ozon import format_string as formating
from utils.api.api import get_product
from .utils import ParserTree

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
        if form.instance.model_list is None and self.text:
            form.instance.model_list = self.text
        clean_shablon_dir(form.instance.xcel_shablon)
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

    def form_valid(self, form):
        clean_shablon_dir(form.instance.xcel_shablon)
        return super().form_valid(form)


class XlFormListView(ListView):
    model = Ozon
    ordering = '-id'
    paginate_by = 20


class Formatter(View):
    template_name = 'ozon/formatter.html'
    text = None

    def get(self, request):
        self.brand, self.sep = formating.get_Separation()
        form = FormatingForm(
            initial={'text': self.text, 'brand': self.brand, 'sep': self.sep})
        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request):
        self.text = formating.get_format_strgin(
            number=self.request.POST['button'],
            text=self.request.POST['text'],
            brand=self.request.POST['brand'],
            sep=self.request.POST['sep']
        )
        self.brand, self.sep = formating.get_Separation()
        form = FormatingForm(
            initial={
                'text': self.text,
                'brand': self.brand,
                'sep': self.sep}
        )
        context = {'form': form}
        return render(request, self.template_name, context)


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

    get_product(
        info.article,
        info.title,
        info.barcode,
        info.image,
    )
    excel_edit(choice_file_xl(info.xcel_shablon))
    return redirect('ozon:detail', pk=info.id)


class CataForm(forms.Form):
    def __init__(self, search_string, categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if search_string:
            result = []
            for cat_id, name in categories:
                if search_string.lower() in name.lower():
                    result.append((cat_id, name))
            if not result:
                result = [(None, 'Не найдено категорий.')]
            self.fields['description_category_id'] = forms.ChoiceField(
                choices=result, widget=forms.Select, help_text='Категория',
                required=False
            )


class DynamicProductForm(forms.Form):
    ...


class FormView(View):
    template_name = 'ozon/test_form.html'
    categories = ParserTree()

    def get(self, request, *args, **kwargs):
        search_form = SearchForm(request.GET)
        search_string = search_form.data.get('cat_search')
        choice_cata = ast.literal_eval(
            search_form.data.get('description_category_id'))

        select_categories = CataForm(
            search_string=search_string,
            categories=self.categories.categories,
        )

        if not search_string:
            return render(request, self.template_name, context={
                'search_form': search_form,
            })

        if choice_cata:
            self.categories.get_atributes(choice_cata)
            select_categories.data = choice_cata

        return render(request, self.template_name, {
                'search_form': search_form,
                'select_categories': select_categories
        })
