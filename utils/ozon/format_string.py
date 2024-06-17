import os

from django.conf import settings


brands = {
    'amica', 'zanussi', 'moulinex', 'aeg', 'hotpoint-ariston', 'privileg',
    'bauknecht', 'constructa', 'rotel', 'beko', 'kenwood', 'electrolux',
    'tefal', 'siemens', 'miele', 'melitta', 'gorenje', 'bosch', 'philips',
    'krups', 'whirlpool', 'lg', 'dolce gusto', 'saeco', 'braun', 'nivona',
    'indesit', 'samsung', 'ariston', 'rowenta', 'philips-saeco', 'maytag',
    'jura', 'delonghi', 'spidem', 'gaggia', 'smeg', 'kitchenaid', 'delfa',
    'hansa', 'zelmer', 'bifinett', 'nespresso'
}

file_path = os.path.join(settings.BASE_DIR, 'utils', 'ozon', 'mem.txt')


def get_Separation():
    with open(file_path, 'r') as get_info:
        information = get_info.readlines()
        brand, separation = [i.rstrip('\n') for i in information]
        return brand, separation


# Проставляем бренды в списке моделей без брендов \\ 1
def brands_by_sep(brand, separation, text):
    string = text
    new_string = ''
    for el in string.split(separation if separation != 'n' else '\n'):
        if el == '':
            continue
        if brand not in el:
            new_string += f'{brand} {el}\n'
            continue
        new_string += f'{el}\n'

    with open(file_path, 'w') as write_info:
        write_info.write(f'{brand}\n{separation}')

    return new_string


def model_list_zipcom(text):  # \\ 2
    string = text
    new_string = ''
    for stroka in string.split('\n'):
        if stroka.split()[0].lower() in brands:
            if stroka not in new_string:
                new_string += f'{stroka}\n'
    new_string = new_string.replace('\t', ' ')
    return new_string


def del_enter(text):  # удаляем лишние переносы строки \\ 3
    models = text.split('\r\n')
    new_string = ''
    for string in models:
        if string == '':
            continue
        new_string += f'{string}\n'
    return new_string


def del_brand(text):  # Удаляем бренды из списка моделей. \\ 4
    string = text
    # Получаем список моделей которые есть в аннотации.
    list_brand = [brand for brand in brands if brand in string]
    string = string.split('\n')
    for brand in list_brand:
        for index in range(len(string)):
            string[index] = string[index].replace(brand + ' ', '')
            string[index] = string[index].replace(brand, '')
            string[index] = string[index].replace(brand + ', ', '')
    result = '\n'.join(string)
    return result


def model_list_doc_cm(text):
    model_list = text.split('\n')
    result: str = ''
    model_actual: str = ''
    for model in model_list:
        if model == '':
            continue
        elif model.lower() in brands:
            model_actual = model.capitalize()
            continue
        result += f'{model_actual} {model}\n'
    return result


def fiyo(text):
    model_list = text.split('\n')
    new_model_list = []
    actual_brand = ''
    count = 0
    for model in model_list:
        if model.lower() in brands:
            if actual_brand != model:
                actual_brand = model
            count += 1
            continue
        if actual_brand and count == 1:
            new_model = f'{actual_brand.capitalize()} {model}'
            if new_model not in new_model_list:
                new_model_list.append(new_model)
        count = 0

    result = '\n'.join(new_model_list)
    return result


def get_format_strgin(number, text, brand=None, sep=None):
    funcs = {
        '1': brands_by_sep,
        '2': model_list_zipcom,
        '3': del_enter,
        '4': del_brand,
        '5': model_list_doc_cm,
        '6': fiyo,
    }
    if number == '1':
        return funcs[number](brand=brand, separation=sep, text=text)
    return funcs[number](text)
