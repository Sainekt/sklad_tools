from reportlab.pdfgen import canvas
from reportlab_qr_code import qr_draw
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

fonts_path = 'static/fonts/'

pdfmetrics.registerFont(TTFont(
    'Noto', fonts_path + 'NotoSans-Regular.ttf'
))
pdfmetrics.registerFont(TTFont('Noto-bold', fonts_path + 'NotoSans-Bold.ttf'))


def draw_name_and_code(product, pdf):
    def get_center(text, size):
        x = 57 * mm / 2 - len(text)*size
        if x < 2:
            x = 5
        return x

    pdf.setFont('Noto', 10)
    result = ''
    x = 2*mm
    y = 40*mm
    for i in range(len(product.name)):
        if i > 100:
            break
        if i % 27 == 0:
            pdf.drawString(x, y, result)
            result = ''
            if y < 26.5:
                y = 26.5
            else:
                y -= 3.4*mm

        result += product.name[i]
    else:
        x = get_center(product.name, 2)
        pdf.drawString(x, y, result)

    pdf.setFont('Noto-bold', 15)
    x = get_center(product.code, 4)
    pdf.drawString(x, 22*mm, product.code)


def draw_date_and_cell(product, pdf, date):
    pdf.setFont('Noto', 8)
    formatted_date = date.strftime("%d-%m")
    pdf.drawString(2, 10, str(formatted_date))
    pdf.setFont('Noto-bold', 10)
    if product.cell_number:
        pdf.drawRightString(44*mm, 10, product.cell_number[:18])


def clear_barcodes(product):
    barcode = product.barcodes
    if barcode == 'None':
        return
    barcods = barcode.split(':')[1]
    barcod = barcods.split("'")[1]
    return barcod


def create_label(data):
    pdf = canvas.Canvas(
        filename='media/pdf/products_label.pdf', pagesize=(57*mm, 40*mm)
    )
    for i in range(len(data)):
        products, iterations = data[i]
        product = products.product
        barcode = clear_barcodes(product)
        for _ in range(iterations):
            if barcode:
                qr_draw(pdf, text=barcode, x='45mm', y='1mm', size='1cm')
                barcode_draw = code128.Code128(
                    barcode, humanReadable=True,
                    barHeight=5*mm, barWidth=0.3*mm
                )
                barcode_draw.drawOn(pdf, x=-2*mm, y=14*mm)
            draw_name_and_code(product, pdf)
            draw_date_and_cell(product, pdf, products.order.created_at)
            pdf.showPage()

        if len(data) > 1:  # если несколько товаров лента разделяется.
            pdf.setFont('Noto-bold', 10)
            pdf.drawCentredString(27*mm, 20*mm, '<<Разделитель>>')
            pdf.showPage()
    pdf.save()
