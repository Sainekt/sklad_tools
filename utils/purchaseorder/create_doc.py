import os
from django.conf import settings
from openpyxl import Workbook


def create_report(data, order):
    work_book = Workbook()
    work_sheet = work_book.active
    work_sheet.title = 'new'
    work_sheet['A1'] = f'Отчет по заказу №: {order.name}'
    work_sheet['A4'] = '№'
    work_sheet['B4'] = 'Наименование'
    work_sheet['C4'] = 'Код'
    work_sheet['D4'] = 'Заказано'
    work_sheet['E4'] = 'ФАКТ'
    work_sheet['F4'] = 'Комментарий'

    row = 5
    index = 0
    while index <= len(data) - 1:
        products = data[index]
        work_sheet[f'A{row+index}'] = index + 1
        work_sheet[f'B{row+index}'] = products.product.name
        work_sheet[f'C{row+index}'] = products.product.code
        work_sheet[f'D{row+index}'] = products.quantity
        work_sheet[f'E{row+index}'] = products.fact
        work_sheet[f'F{row+index}'] = products.comment

        index += 1

    file_path = os.path.join(
        settings.MEDIA_ROOT, 'purchaseorder_doc',
        f'Отчет_по_заказу_{order.name}.xlsx'
    )

    a = work_book.save(file_path)
    order.xl_doc = file_path
    order.save()
