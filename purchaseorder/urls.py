from django.urls import path
from . import views

app_name = 'purchaseorder'

urlpatterns = [
    path('', views.OrderList.as_view(), name='main'),
    path('order/<slug:slug>/', views.OrderPositions.as_view(), name='order'),
    path(
        'create_doc/<slug:slug>/',
        views.CreateOrderDoc.as_view(),
        name='create_doc',
    ),
]
