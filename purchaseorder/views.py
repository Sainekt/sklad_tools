import os
from dotenv import load_dotenv
import requests
import json

from django.views import generic

load_dotenv()

TOKEN = os.getenv('token')
if not TOKEN:
    raise ValueError('Требуется токен Моего скалада.')

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-type': 'application/json'
}

PARAMS = (('limit', 50),)

# from .models import
# from .forms import ScannerForm, MarketForm


class ResponseMixin(generic.TemplateView):
    @staticmethod
    def response(url, headers=HEADERS, params=PARAMS):
        return requests.get(
            url=url,
            headers=headers,
            params=params
        )


class OrderList(ResponseMixin):
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


class OrderPositions(ResponseMixin):
    template_name = 'purchaseorder/order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_positions()
        context["context"] = self.positions
        context['number'] = self.number
        return context

    def get_positions(self):
        pk = self.kwargs['slug']
        url = (f'https://api.moysklad.ru/api/remap/1.2/entity/purchaseorder/{pk}')
        self.number = self.response(url).json()
        url += '/positions?expand=assortment'
        response = self.response(url, params=None).json()['rows']
        print(len(response))
        self.positions = response
