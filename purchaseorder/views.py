import os
from dotenv import load_dotenv
import requests
from django.shortcuts import redirect, get_object_or_404

from django.views import generic, View
from django.db import transaction
from pytils.translit import slugify

from .models import PurchaseOrder, Order
# from .forms import ScannerForm, MarketForm

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
            Order.objects.get(name=order_name)
            return redirect('purchaseorder:document', order_name)

        except Order.DoesNotExist:
            order = Order.objects.create(name=order_name)

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


class OrderDoc(generic.ListView):
    template_name = 'purchaseorder/create_doc.html'
    model = Order

    def get_queryset(self):
        return get_object_or_404(
            self.model, name=self.kwargs['slug']
        ).products.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['number'] = self.kwargs['slug']
        return context
