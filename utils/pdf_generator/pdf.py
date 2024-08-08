from reportlab.pdfgen import canvas
from reportlab_qr_code import qr_draw
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('Noto', 'NOTOSANS-REGULAR.ttf'))
pdfmetrics.registerFont(TTFont('Noto-bold', 'NOTOSANS-BOLD.ttf'))


data = '123654789123615'

pdf = canvas.Canvas(filename='output.pdf', pagesize=(57*mm, 40*mm))
qr_draw(pdf, text=data, x='45mm', y='1mm', size='1cm')

# Создаем объект штрих-кода с необходимыми параметрами
barcode = code128.Code128(data, humanReadable=True)  # Отображаем текст под штрих-кодом
barcode.barHeight = 5*mm  # Устанавливаем высоту штрих-кода
barcode.barWidth = 0.3*mm  # Устанавливаем ширину штрих-кода
barcode.drawOn(pdf, x=-2*mm, y=14*mm)


def draw_name_and_code(text, pdf, code):
    def get_center(text, size):
        x = 57 * mm / 2 - len(text)*size
        if x < 1:
            x = 1
        return x

    pdf.setFont('Noto', 10)
    result = ''
    x = 2*mm
    y = 40*mm
    print(len(text))
    for i in range(len(text)):
        if i > 100:
            break
        if i % 27 == 0:
            pdf.drawString(x, y, result)
            result = ''
            y -= 10
        result += text[i]
    else:
        x = get_center(text, 2)
        pdf.drawString(x, y, result)

    pdf.setFont('Noto-bold', 15)
    x = get_center(code, 4)
    pdf.drawString(x, 22*mm, code)


def draw_date_and_cell(date, pdf, cell):
    pdf.setFont('Noto', 8)
    x, y = 2, 10
    pdf.drawString(x, y, date)
    pdf.setFont('Noto-bold', 10)
    x, y = 25, 10
    pdf.drawString(x, y, cell[:18])


data = 'Какой то очень длинный текст для гребанной наклейки, но за то по идее она должна формироваться очень быстро а еще на ней есть qr-code все для этого, ну еще немного опыта. '
code = "A2000-AKS-"
draw_name_and_code(data, pdf, code)

date = '31.08'
cell = 'Б-6 А-1 и пошел нахуй'

draw_date_and_cell(date, pdf, cell)
pdf.showPage()
pdf.save()
