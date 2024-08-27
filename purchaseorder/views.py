import os
from dotenv import load_dotenv
import requests
from django.shortcuts import redirect, get_object_or_404, render
from django.conf import settings
from django.urls import reverse_lazy
from django.http import HttpResponse, Http404
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from django.views import generic, View
from django.db import transaction
from django.forms import modelformset_factory
from pytils.translit import slugify

from .models import PurchaseOrder, Order, Product
from .forms import ProductForm, FactForm, DetailLabelForm
from utils.purchaseorder.label_generator import (
    create_label, create_user_label)
from utils.purchaseorder.create_doc import create_report

load_dotenv()

TOKEN = os.getenv('ms_token')
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


class DetailUpdateMixin(ResponseMixin):
    url = 'https://api.moysklad.ru/api/remap/1.2/entity/product/'

    def get_postition(self, pk):
        response = self.response(self.url + pk + '/?expand=images')
        if response.status_code != 200:
            return
        return response

    def get_valid_info(self, response):
        miniature = 'purchaseorder/preview.jpg'
        image = 'purchaseorder/previewBIG.jpg'
        resp = response.json()
        pk = resp.get('id')
        name = resp.get('name')
        if not pk or not name:
            return
        code = resp.get('code')
        article = resp.get('article')
        barcodes = resp.get('barcodes')
        attributes = resp.get('attributes')
        description = resp.get('description')
        cell = ListCreatePositionsDocMixin.get_cell(attributes)
        miniature_resp = resp.get('images').get('rows')
        if miniature_resp:
            miniature_url = miniature_resp[0]['miniature']['downloadHref']
            miniature = ListCreatePositionsDocMixin.download_image(
                pk, miniature_url
            )
            image = self.download_big_size_photo(resp)
        return (
            pk, name, code, article, barcodes, cell, miniature, image,
            description,
        )

    def download_big_size_photo(self, response):
        try:
            pk = response['id']
            images = response['images']['rows']
            images_download_url = images[0]['meta']['downloadHref']
        except LookupError:
            return
        image = ListCreatePositionsDocMixin.download_image(
            pk, images_download_url, 'BIG'
        )
        return image


class ListCreatePositionsDocMixin:

    def get_positions(self):
        pk = self.kwargs['slug']
        url = (
            f'https://api.moysklad.ru/api/remap/1.2/entity/purchaseorder/{pk}'
        )
        self.number = self.response(url).json()
        url += '/positions?expand=assortment.images'
        dict_response = self.response(url, params=None).json()
        response = dict_response.get('rows')
        errors = dict_response.get('errors')
        if errors:
            error = errors[0].get('error')
            raise Http404(f'Ответ моего склада вернул: {error}')
        self.positions_quantity = len(response)
        self.positions = response

    @staticmethod
    def get_cell(cell_attr):
        cell_id = '17bbadc0-786b-11ec-0a80-06bd004b0ee2'
        cell_value = ''
        if cell_attr:
            for cell in cell_attr:
                if cell['id'] == cell_id:
                    cell_value = cell['value']

        return cell_value

    def get_valid_data(self, info):
        if not (product_id := info['assortment'].get('id')):
            raise ValueError('ID товара не получено от Моего склада.')
        name = info['assortment'].get('name')
        barcodes = None
        if barcodes := info['assortment'].get('barcodes'):
            barcodes = str(barcodes)
        code = info['assortment'].get('code')
        article = info['assortment'].get('article')
        cell_attr = info['assortment'].get('attributes')
        cell_number = self.get_cell(cell_attr)
        description = info['assortment'].get('description')
        return (
            product_id, name, barcodes, code, article, cell_number,
            description
        )

    def get_image(self, info):
        product_id = info['assortment'].get('id')
        miniature_url = info['assortment']['images'].get('rows')
        image_miniature = 'purchaseorder/preview.jpg'
        if miniature_url:
            miniature_url = (
                miniature_url[0].get('miniature').get('downloadHref'))
            image_miniature = (
                self.download_image(product_id, miniature_url)
                or image_miniature)
        return image_miniature

    @staticmethod
    def download_image(product_id, image_url, prefix=''):
        response = requests.get(image_url, headers=HEADERS, stream=True)
        if response.status_code != 200:
            return

        content_type = response.headers.get('Content-Type')
        if content_type:
            extension = '.' + content_type.split('/')[1]
        else:
            return

        file_path = os.path.join(
            settings.MEDIA_ROOT,
            'purchaseorder', product_id + prefix + extension)
        media_path = 'purchaseorder/' + product_id + prefix + extension

        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        return media_path


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
            error = dict_response.get('errors')[0].get('error')
            raise Http404(f'Ответ моего склада вернул: {error}')
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
        context["back_page"] = self.request.META.get('HTTP_REFERER')
        return context


class CreateOrderDoc(
    ResponseMixin,
    ListCreatePositionsDocMixin,
    View
):
    @method_decorator(ratelimit(key='ip', rate='1/1m', method='POST'))
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
             code, article, cell_number,
             description) = self.get_valid_data(info)
            try:
                product = Product.objects.get(
                    product_id=product_id
                )
                if (product.name != name
                        or product.barcodes != barcodes
                        or product.code != code
                        or product.article != article
                        or product.cell_number != cell_number
                        or product.description != description):
                    product.name = name
                    product.barcodes = barcodes
                    product.code = code
                    product.article = article
                    product.cell_number = cell_number
                    product.description = description
                    product.save()
            except Product.DoesNotExist:
                miniature = self.get_image(info)
                product = Product.objects.create(
                        product_id=product_id,
                        name=name,
                        barcodes=barcodes,
                        code=code,
                        article=article,
                        cell_number=cell_number,
                        miniature=miniature,
                        description=description,
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

    @method_decorator(ratelimit(key='ip', rate='1/5s', method='POST'))
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
            'MEDIA_URL': settings.MEDIA_URL
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
                plus = abs(int(data[info]))
                if plus > 1000:
                    raise ValueError('Значение не может быть больше 1000')
                product.fact += plus
                fact_updates.append(product)
                labels.append((product, plus))
            if 'comment' in info:
                if data[info] != product.comment:
                    product.comment = data[info][:250]
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


class DocUpdateProductFactView(generic.UpdateView):
    model = PurchaseOrder
    form_class = FactForm

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('purchaseorder:document', kwargs={'slug': slug})


class DocUpdateProducts(ResponseMixin, ListCreatePositionsDocMixin, View):

    @method_decorator(ratelimit(key='ip', rate='1/1m', method='POST'))
    def post(self, request, *args, **kwargs):
        self.get_positions()
        order_name = slugify(self.number['name'])
        order = get_object_or_404(Order, slug=order_name)

        with transaction.atomic():
            for info in self.positions:
                (product_id, name, barcodes,
                 code, article, cell_number,
                 description, ) = self.get_valid_data(info)
                miniature = self.get_image(info)
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
                        cell_number=cell_number,
                        miniature=miniature,
                        description=description,
                    )
                else:
                    product.name = name
                    product.barcodes = barcodes
                    product.code = code
                    product.article = article
                    product.cell_number = cell_number
                    product.miniature = miniature
                    product.description = description
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


class ProductDetail(DetailUpdateMixin, generic.DetailView):
    template_name = 'purchaseorder/product_detail.html'
    model = Product

    def get_object(self):
        return get_object_or_404(
            self.model, product_id=self.kwargs[self.slug_url_kwarg]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["MEDIA_URL"] = settings.MEDIA_URL
        context["back_page"] = self.request.META.get('HTTP_REFERER')
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not self.object.image:
            response = self.get_postition(self.object.product_id)
            if response:
                photo_path = self.download_big_size_photo(response.json())
                self.object.image = photo_path
                self.object.save()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class ProductUpdateView(DetailUpdateMixin, View):

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, product_id=kwargs['slug'])
        position = self.get_postition(kwargs['slug'])
        if not position:
            raise Http404('Товар с таким id не найден на сайте Мой Склад')
        (pk, name, code, article,
         barcodes, cell, miniature,
         image, description) = self.get_valid_info(position)
        if pk != kwargs['slug']:
            return ValueError('ID из МС не совпадает с запрошеным ID')
        product.name = name
        product.code = code
        product.article = article
        product.barcodes = barcodes
        product.cell_number = cell
        product.miniature = miniature
        product.image = image
        product.description = description
        product.save()
        return redirect('purchaseorder:product_detail', kwargs['slug'])


def download_label(request, file_name='products_label'):
    file_path = os.path.join(
        settings.BASE_DIR, 'media', 'pdf', f'{file_name}.pdf'
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
        context["MEDIA_URL"] = settings.MEDIA_URL
        context["back_page"] = self.request.META.get('HTTP_REFERER')
        return context


class ProductCreateLabelForm(generic.UpdateView):
    """Для создания этикетки с нужной информацией"""
    form_class = DetailLabelForm
    model = Product
    template_name = 'purchaseorder/product_detail_form.html'

    def form_valid(self, form):
        obj = self.get_object()
        obj.name = form.instance.name
        obj.code = form.instance.code
        obj.barcodes = form.instance.barcodes
        obj.cell_number = form.instance.cell_number
        create_user_label(obj, form.cleaned_data['date'])
        response = download_label(None, obj.product_id)
        file_path = os.path.join(
            settings.BASE_DIR, 'media', 'pdf', f'{obj.product_id}.pdf'
        )
        os.remove(file_path)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_page"] = self.request.META.get('HTTP_REFERER')
        return context
