from django.urls import path

from . import views

app_name = 'ozon'

urlpatterns = [
    path('', views.XlFormCreateView.as_view(), name='form')
]
