from django.urls import path
from . import views

app_name = 'ozon'

urlpatterns = [
    path('', views.XlFormCreateView.as_view(), name='form'),
    path("<int:pk>/", views.XlFormDetailView.as_view(), name="detail"),
    path("edit/<int:pk>/", views.XlFormUpdateView.as_view(), name="edit"),
    path('list/', views.XlFormListView.as_view(), name='list'),
    path('edit_xl/<int:pk>/', views.edit_xl, name='edit_xl'),
    path('formatter/', views.Formatter.as_view(), name='formatter'),

]
