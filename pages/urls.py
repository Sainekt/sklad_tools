from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.Home.as_view(), name='home')
]
