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
    path('document/<slug:slug>/', views.OrderDoc.as_view(), name='document'),
    path('documents/', views.DocListViews.as_view(), name='doc_list'),
    path(
        'document/<int:pk>/delete/',
        views.DocDeleteView.as_view(),
        name='doc_delete'
    ),
    path(
        'product/<int:pk>/update/<slug:slug>/',
        views.DocUpdateView.as_view(),
        name='product_update'
    )
]
