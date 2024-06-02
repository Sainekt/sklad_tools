from django.urls import path
from . import views

app_name = 'scanner'

urlpatterns = [
    path('', views.ScannerPage.as_view(), name='main'),
    path('pik/', views.ScannerCreate.as_view(), name='pik'),
    path(
        'market_create/',
        views.MarketPlaceCreate.as_view(),
        name='market_create'
    ),


]
