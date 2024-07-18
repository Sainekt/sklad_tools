from django.urls import path
from . import views

app_name = 'purchaseorder'

urlpatterns = [
    path('', views.OrderList.as_view(), name='main'),
    # path('pik/', views.ScannerCreate.as_view(), name='order'),
]
