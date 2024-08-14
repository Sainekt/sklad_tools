import os
from dotenv import load_dotenv
import requests
from django.shortcuts import redirect, get_object_or_404, render
from django.conf import settings
from django.urls import reverse_lazy
from django.http import HttpResponse, Http404

from django.views import generic, View
from django.db import transaction
from django.forms import modelformset_factory
from pytils.translit import slugify

from .models import PurchaseOrder, Order, Product
from .forms import ProductForm, FactForm
from utils.purchaseorder.label_generator import create_label
from utils.purchaseorder.create_doc import create_report

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
    cell_id = '17bbadc0-786b-11ec-0a80-06bd004b0ee2'

    def get_positions(self):
        pk = self.kwargs['slug']
        url = (
            f'https://api.moysklad.ru/api/remap/1.2/entity/purchaseorder/{pk}'
        )
        self.number = self.response(url).json()
        url += '/positions?expand=assortment'
        dict_response = self.response(url, params=None).json()
        response = dict_response.get('rows')
        if not response:
            raise Http404(
                f'Ответ моего склада вернул: '
                f'{dict_response.get('errors')[0].get('error')}'
            )
        self.positions_quantity = len(response)
        self.positions = response

    def get_cell(self, info):
        cell_attr = info['assortment'].get('attributes')
        cell_value = ''
        if cell_attr:
            for cell in cell_attr:
                if cell['id'] == self.cell_id:
                    cell_value = cell['value']

        return cell_value

    def get_valid_data(self, info):
        if not (product_id := info['assortment'].get('id')):
            raise ValueError('ID товара не получено от Моего склада.')
        name = info['assortment'].get('name')
        barcodes = str(info['assortment'].get('barcodes'))
        code = info['assortment'].get('code')
        article = info['assortment'].get('article')
        cell_number = self.get_cell(info)
        return product_id, name, barcodes, code, article, cell_number


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
        dict_response = self.response(url).json()
        response = dict_response.get('rows')
        if not response:
            raise Http404(
                f'Ответ моего склада вернул: '
                f'{dict_response.get('errors')[0].get('error')}'
            )
        self.order_list = response


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

        try:
            order_object = Order.objects.get(order_id=self.kwargs['slug'])
            return redirect('purchaseorder:document', order_object.slug)

        except Order.DoesNotExist:
            self.get_positions()
            object_to_create = []
            order_name = slugify(self.number['name'])
            order = Order.objects.create(
                name=self.number['name'], slug=order_name,
                order_id=self.number['id'])

        for info in self.positions:
            (product_id, name, barcodes,
             code, article, cell_number) = self.get_valid_data(info)
            try:
                product = Product.objects.get(
                    product_id=product_id
                )
            except Product.DoesNotExist:
                product = Product.objects.create(
                        product_id=product_id,
                        name=name,
                        barcodes=barcodes,
                        code=code,
                        article=article,
                        cell_number=cell_number
                )
            new_obj = PurchaseOrder(
                order=order,
                quantity=info['quantity'],
                summ=info['price'],
                fact=0,
                product=product
            )

            object_to_create.append(new_obj)
        with transaction.atomic():
            PurchaseOrder.objects.bulk_create(object_to_create)

        return redirect('purchaseorder:document', order_name)


class UpdateOrderDoc(View):
    """Работа с документом."""
    template_name = 'purchaseorder/create_doc.html'

    def get(self, request, slug):
        order, formset = self.get_data(request, slug)
        context = self.get_context(formset, order)
        return render(request, self.template_name, context=context)

    def post(self, request, slug):
        self.get_data(request, slug)
        return redirect('purchaseorder:document', slug)

    def get_data(self, request, slug):
        order = get_object_or_404(Order, slug=slug)
        order_positions = order.products.select_related('order', 'product')
        if request_post := request.POST:
            data = {}
            for i in request_post:
                if i == 'csrfmiddlewaretoken':
                    continue
                if request_post[i]:
                    data[i] = request_post[i]
            if data:
                self.update_order_doc(data, order_positions)
            return

        ProductFormset = modelformset_factory(
            PurchaseOrder, form=ProductForm, extra=0
        )
        formset = ProductFormset(queryset=order_positions)
        return order, formset

    @staticmethod
    def get_context(formset, order):
        context = {
            'order': order,
            'product_formset': formset,
            'len_doc': len(formset),
        }
        return context

    def update_order_doc(self, data: dict, order_positions):
        fact_updates = []
        comment_updates = []
        labels = []

        for info in data:
            index = int(info.split('-')[1])
            product = order_positions[index]
            if 'plus' in info:
                plus = int(data[info])
                product.fact += plus
                fact_updates.append(product)
                labels.append((product, plus))
            if 'comment' in info:
                if data[info] != product.comment:
                    product.comment = data[info]
                    comment_updates.append(product)

        if fact_updates:
            PurchaseOrder.objects.bulk_update(fact_updates, ['fact'])
            create_label(labels)

        if comment_updates:
            PurchaseOrder.objects.bulk_update(comment_updates, ['comment'])


class DocListViews(generic.ListView):
    model = Order
    ordering = '-id'
    paginate_by = 10


class DocDeleteView(generic.DeleteView):
    model = Order
    success_url = reverse_lazy('purchaseorder:doc_list')


class DocUpdateProductView(generic.UpdateView):
    model = PurchaseOrder
    form_class = FactForm

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('purchaseorder:document', kwargs={'slug': slug})


class DocUpdateProducts(ResponseMixin, ListCreatePositionsDocMixin, View):
    def post(self, request, *args, **kwargs):
        self.get_positions()
        order_name = slugify(self.number['name'])
        order = get_object_or_404(Order, slug=order_name)

        with transaction.atomic():
            for info in self.positions:
                (product_id, name, barcodes,
                 code, article, cell_number) = self.get_valid_data(info)
                try:
                    product = Product.objects.get(
                        product_id=product_id
                    )
                except Product.DoesNotExist:
                    product = Product.objects.create(
                        product_id=product_id,
                        name=name,
                        barcodes=barcodes,
                        code=code,
                        article=article,
                        cell_number=cell_number
                    )
                else:
                    product.name = name
                    product.barcodes = barcodes
                    product.code = code
                    product.article = article
                    product.cell_number = cell_number
                    product.save()

                # Обновление или создание записи в PurchaseOrder
                try:
                    purchase_order = PurchaseOrder.objects.get(
                        order=order,
                        product=product,
                    )
                except PurchaseOrder.DoesNotExist:
                    purchase_order = PurchaseOrder(
                        order=order,
                        product=product,
                    )
                except PurchaseOrder.MultipleObjectsReturned:
                    continue
                purchase_order.quantity = info['quantity']
                purchase_order.summ = info['price']
                purchase_order.save()

        return redirect('purchaseorder:document', order_name)


def download_label(request):
    file_path = os.path.join(
        settings.BASE_DIR, 'media', 'pdf', 'products_label.pdf'
    )
    with open(file_path, 'rb') as file:
        response = HttpResponse(
            file.read(), content_type="application/pdf"
        )
        response['Content-Disposition'] = (
            'attachment; filename="products_label.pdf"'
        )
        return response


class CreateDownloadXcelDoc(View):
    template_name = 'purchaseorder/create_download_xcel.html'

    def get(self, request, *args, **kwargs):
        self.order = Order.objects.get(order_id=kwargs['slug'])
        self.order_positions = (
            self.order.products.select_related('order', 'product')
        )
        create_report(self.order_positions, self.order)
        context = self.get_context_data()
        return render(request, self.template_name, context=context)

    def get_context_data(self, **kwargs):
        context = {}
        context["order"] = self.order
        context["count_product"] = len(self.order_positions)
        return context
