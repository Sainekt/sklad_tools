import requests
import os
from dotenv import load_dotenv
from django.conf import settings
import json


load_dotenv()

API_KEY = os.getenv('Api-Key')
CLIENT_ID = os.getenv('Client-Id')

HEADERS = {
    'Client-Id': CLIENT_ID,
    'Api-Key': API_KEY
}

URL = 'https://api-seller.ozon.ru/v1/description-category/tree'

CATEGORIES = requests.post(
    url=URL,
    headers=HEADERS,
    data=None,

).json()


class ParserTree:
    def __init__(self):
        self.categories: list = self.get_cata_v1(CATEGORIES)

    def get_cata_v1(self, response):
        data = []
        for cata_v2 in response['result']:
            if cats_v2 := cata_v2.get('children'):
                for cata_v1 in cats_v2:
                    cata_v3_id = cata_v1['description_category_id']
                    if cats_v1 := cata_v1.get('children'):
                        for type_v3 in cats_v1:
                            data.append((
                                (
                                    cata_v3_id,
                                    type_v3['type_id']
                                ),
                                type_v3['type_name']
                            ))
        return data

    def get_atributes(self, category: tuple):
        cat_id, type_id = (53968796, 970707394)
        url = 'https://api-seller.ozon.ru/v1/description-category/attribute'
        data = json.dumps({
            'description_category_id': cat_id,
            'type_id': type_id
        })
        attributes = requests.post(
            url=url,
            data=data,
            headers=HEADERS
        ).json().get('result')
        if not attributes:
            raise ValueError('Не нашлись атрибуты категории.')
        self.attribures = attributes
