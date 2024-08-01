import os
from dotenv import load_dotenv
import requests
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy

from django.views import generic, View
from django.db import transaction
from django.forms import modelformset_factory
from pytils.translit import slugify

from .models import PurchaseOrder, Order
from .forms import ProductForm, FactForm

load_dotenv()

TOKEN = os.getenv('token')
if not TOKEN:
    raise ValueError('Требуется токен Моего скалада.')

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-type': 'application/json'
}

PARAMS = (('limit', 50),)


class ResponseMixin:
    @staticmethod
    def response(url, headers=HEADERS, params=PARAMS):
        return requests.get(
            url=url,
            headers=headers,
            params=params
        )


class ListCreatePositionsDocMixin:
    def get_positions(self):
        pk = self.kwargs['slug']
        url = (
            f'https://api.moysklad.ru/api/remap/1.2/entity/purchaseorder/{pk}'
        )
        self.number = self.response(url).json()
        url += '/positions?expand=assortment'
        response = self.response(url, params=None).json()['rows']
        self.positions_quantity = len(response)
        self.positions = response


class OrderList(ResponseMixin, generic.TemplateView):
    template_name = 'purchaseorder/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_order_list()
        context["order_list"] = self.order_list
        return context

    def get_order_list(self):
        url = ('https://api.moysklad.ru/api/remap/1.2/entity/purchaseorder'
               '?order=created,desc&expand=agent')
        response = self.response(url)
        self.order_list = response.json()['rows']


class OrderPositions(
    ResponseMixin,
    ListCreatePositionsDocMixin,
    generic.TemplateView
):
    template_name = 'purchaseorder/order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_positions()
        context["context"] = self.positions
        context['number'] = self.number
        context['positions_quantity'] = self.positions_quantity
        return context


class CreateOrderDoc(
    ResponseMixin,
    ListCreatePositionsDocMixin,
    View
):
    def post(self, request, *args, **kwargs):
        self.get_positions()
        object_to_create = []
        order_name = slugify(self.number['name'])

        try:
            Order.objects.get(slug=order_name)
            return redirect('purchaseorder:document', order_name)

        except Order.DoesNotExist:
            order = Order.objects.create(
                name=self.number['name'], slug=order_name)

        for info in self.positions:
            barcodes = str(info['assortment'].get('barcodes'))
            new_obj = PurchaseOrder(
                name=info['assortment']['name'],
                order=order,
                code=info['assortment']['code'],
                barcodes=barcodes,
                quantity=info['quantity'],
                summ=info['price'],
                fact=0,
            )
            object_to_create.append(new_obj)
        with transaction.atomic():
            PurchaseOrder.objects.bulk_create(object_to_create)

        return redirect('purchaseorder:document', order_name)


class OrderDoc(View):
    """Работа с документом."""
    template_name = 'purchaseorder/create_doc.html'

    def get(self, request, slug):
        order = get_object_or_404(Order, slug=slug)
        products = order.products.all()

        ProductFormSet = modelformset_factory(
            PurchaseOrder, form=ProductForm, extra=0
        )
        formset = ProductFormSet(queryset=products, prefix='')
        context = {
            'number': order.name,
            'product_formset': formset,
            'len_doc': len(products),
            'order_slug': order.slug

        }
        return render(request, self.template_name, context=context)

    def post(self, request, slug):
        order = get_object_or_404(Order, slug=slug)
        products = order.products.all()

        ProductFormset = modelformset_factory(
            PurchaseOrder, form=ProductForm, extra=0
        )
        request_post = request.POST
        data = {}
        for i in request_post:
            if i == 'csrfmiddlewaretoken':
                continue
            if request_post[i]:
                data[i] = request_post[i]

        self.update_order_doc(data, products)
        formset = ProductFormset(queryset=products)
        context = {
            'number': order.name,
            'product_formset': formset,
            'len_doc': len(products),
            'order_slug': order.slug
        }
        return render(request, self.template_name, context=context)

    def update_order_doc(self, data, products):
        fact_updates = []
        comment_updates = []

        for info in data:
            index = int(info.split('-')[1])
            product = products[index]
            if 'plus' in info:
                product.fact += int(data[info])
                fact_updates.append(product)
            if 'comment' in info:
                product.comment = data[info]
                comment_updates.append(product)

        if fact_updates:
            PurchaseOrder.objects.bulk_update(fact_updates, ['fact'])

        if comment_updates:
            PurchaseOrder.objects.bulk_update(comment_updates, ['comment'])


class DocListViews(generic.ListView):
    model = Order
    ordering = '-id'
    paginate_by = 10


class DocDeleteView(generic.DeleteView):
    model = Order
    success_url = reverse_lazy('purchaseorder:doc_list')


class DocUpdateView(generic.UpdateView):
    model = PurchaseOrder
    form_class = FactForm

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('purchaseorder:document', kwargs={'slug': slug})
