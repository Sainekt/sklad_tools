from openpyxl import Workbook
from openpyxl.styles import PatternFill

GREEN_FILL = PatternFill(
    start_color='32cd32', end_color='32cd32', fill_type='solid'
)
YELLOW_FILL = PatternFill(
    start_color='ffff00', end_color='ffff00', fill_type='solid'
)
GRAY_FILL = PatternFill(
    start_color='cccccc', end_color='cccccc', fill_type='solid'
)

BLUE_FILL = PatternFill(
    start_color='33ccff', end_color='33ccff', fill_type='solid'
)


def create_report(data, order):
    work_book = Workbook()
    work_sheet = work_book.active
    work_sheet.title = 'new'
    work_sheet['A1'] = f'Отчет по заказу №: {order.name}'
    work_sheet['B3'] = 'Обозначение цветов:'
    work_sheet['C3'] = 'OK'
    work_sheet['D3'] = 'Больше'
    work_sheet['E3'] = 'Меньше'
    work_sheet['C3'].fill = GREEN_FILL
    work_sheet['D3'].fill = BLUE_FILL
    work_sheet['E3'].fill = YELLOW_FILL

    work_sheet['A7'] = '№'
    work_sheet['B7'] = 'Наименование'
    work_sheet['C7'] = 'Код'
    work_sheet['D7'] = 'Заказано'
    work_sheet['E7'] = 'ФАКТ'
    work_sheet['F7'] = 'Комментарий'

    work_sheet['A7'].fill = GRAY_FILL
    work_sheet['B7'].fill = GRAY_FILL
    work_sheet['C7'].fill = GRAY_FILL
    work_sheet['D7'].fill = GRAY_FILL
    work_sheet['E7'].fill = GRAY_FILL
    work_sheet['F7'].fill = GRAY_FILL

    row = 8
    index = 0
    ok_count = 0
    count_positions = len(data)
    while index <= count_positions - 1:
        products = data[index]
        if products.fact == products.quantity:
            work_sheet[f'A{row+index}'].fill = GREEN_FILL
            work_sheet[f'B{row+index}'].fill = GREEN_FILL
            work_sheet[f'C{row+index}'].fill = GREEN_FILL
            work_sheet[f'D{row+index}'].fill = GREEN_FILL
            work_sheet[f'E{row+index}'].fill = GREEN_FILL
            work_sheet[f'F{row+index}'].fill = GREEN_FILL
            ok_count += 1
        elif products.fact > products.quantity:
            work_sheet[f'A{row+index}'].fill = BLUE_FILL
            work_sheet[f'B{row+index}'].fill = BLUE_FILL
            work_sheet[f'C{row+index}'].fill = BLUE_FILL
            work_sheet[f'D{row+index}'].fill = BLUE_FILL
            work_sheet[f'E{row+index}'].fill = BLUE_FILL
            work_sheet[f'F{row+index}'].fill = BLUE_FILL
        else:
            work_sheet[f'A{row+index}'].fill = YELLOW_FILL
            work_sheet[f'B{row+index}'].fill = YELLOW_FILL
            work_sheet[f'C{row+index}'].fill = YELLOW_FILL
            work_sheet[f'D{row+index}'].fill = YELLOW_FILL
            work_sheet[f'E{row+index}'].fill = YELLOW_FILL
            work_sheet[f'F{row+index}'].fill = YELLOW_FILL

        work_sheet[f'A{row+index}'] = index + 1
        work_sheet[f'B{row+index}'] = products.product.name
        work_sheet[f'C{row+index}'] = products.product.code
        work_sheet[f'D{row+index}'] = products.quantity
        work_sheet[f'E{row+index}'] = products.fact
        work_sheet[f'F{row+index}'] = products.comment

        index += 1

    work_sheet['A5'] = (
        f'В результате приемки сошлось {ok_count} '
        f'позиции из {count_positions}'
    )

    save_path = f'media/purchaseorder_doc/Отчет_по_заказу_{order.name}.xlsx'
    file_path = f'purchaseorder_doc/Отчет_по_заказу_{order.name}.xlsx'
    work_book.save(save_path)
    work_book.close()
    order.xl_doc = file_path
    order.save()
