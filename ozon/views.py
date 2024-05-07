from django.views.generic import CreateView

from .forms import OzonForm
from .models import Ozon


class XlFormCreateView(CreateView):
    model = Ozon
    form_class = OzonForm