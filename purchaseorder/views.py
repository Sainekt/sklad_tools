import os
from dotenv import load_dotenv
import requests

from django.views import generic

load_dotenv()

TOKEN = os.getenv('token')
if not TOKEN:
    raise ValueError('Требуется токен Моего скалада.')

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-type': 'application/json'
}

PARAMS = (('limit', 1),)

# from .models import
# from .forms import ScannerForm, MarketForm


class OrderList(generic.TemplateView):
    template_name = 'purchaseorder/main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_order_list()
        context["order_list"] = self.order_list
        return context

    def get_order_list(self):
        url = ('https://api.moysklad.ru/api/remap/1.2/entity/purchaseorder'
               '?order=created,desc')
        response = self.response(url)
        self.order_list = response.json()['rows']

    @staticmethod
    def response(url, headers=HEADERS, params=PARAMS):
        return requests.get(
            url=url,
            headers=headers,
            params=params
        )
