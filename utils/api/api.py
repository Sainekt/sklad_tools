import requests
import json
import os
import base64

from django.conf import settings
from env import token

HEADERS = {
    'Authorization': f'Bearer {token}',
    'Content-type': 'application/json'
}


def get_product(code, name, barcode, image=None):
    url = 'https://api.moysklad.ru/api/remap/1.2/entity/product'
    params = (('filter', f'code={code}'),)
    response = get_response('GET', url, HEADERS, params)
    if response.status_code == 200:
        url_product = response.json()['rows'][0]['id']
        product_put(url_product, name, barcode, image)
    else:
        print('api Ошибка запроса. Товар не найден.')


def product_put(pk, name, barcode, image=None):
    url = f'https://api.moysklad.ru/api/remap/1.2/entity/product/{pk}'
    body = {
        'name': name,
        'barcodes': [{
            'code128': barcode
        }],
    }
    if image:
        img_name, img_code = get_base64_image(image)
        img_block = {
            'images': [{
                'filename': img_name,
                'content': img_code
            }]
        }
        body |= img_block

    response = get_response('PUT', url, HEADERS, body=body)
    print(f'api status code: {response.status_code}')


def get_response(typ, url, headers=HEADERS, params=None, body=None):
    request_type = {
        'GET': requests.get,
        'PUT': requests.put
    }
    return request_type[typ](
        url=url,
        headers=headers,
        data=json.dumps(body),
        params=params
    )


def get_base64_image(image) -> str:
    name = image.name.split('/')[1]
    image_path = os.path.join(settings.BASE_DIR, 'media', image.name)
    with open(image_path, 'rb') as image_file:
        image = base64.b64encode(image_file.read())
    return name, image.decode('ascii')
