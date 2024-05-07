from django.urls import path

from . import views

app_name = 'ozon'

urlpatterns = [
    path('', views.XlFormCreateView.as_view(), name='form'),
    path("<int:pk>/", views.XlFormDetailView.as_view(), name="detail")
]
