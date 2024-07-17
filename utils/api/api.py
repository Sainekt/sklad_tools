import requests
import json

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
        product_put(url_product, name, barcode)
    else:
        print('api Ошибка запроса. Товар не найден.')


def product_put(pk, name, barcode, image=None):
    url = f'https://api.moysklad.ru/api/remap/1.2/entity/product/{pk}'
    body = {
        'name': name,
        'barcodes': [{
            'code128': barcode
        }]
    }
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
