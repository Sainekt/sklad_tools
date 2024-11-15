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
    path(
        'document/<slug:slug>/',
        views.UpdateOrderDoc.as_view(),
        name='document'
    ),
    path('documents/', views.DocListViews.as_view(), name='doc_list'),
    path(
        'document/<int:pk>/delete/',
        views.DocDeleteView.as_view(),
        name='doc_delete'
    ),
    path(
        'product/<int:pk>/update/<slug:slug>/',
        views.DocUpdateProductFactView.as_view(),
        name='product_update_fact'
    ),
    path('document/<slug:slug>/products_update',
         views.DocUpdateProducts.as_view(), name='update_products'),
    path('product/detail/<slug:slug>/',
         views.ProductDetail.as_view(), name='product_detail'),
    path('product/detail/<slug:slug>/update',
         views.ProductUpdateView.as_view(), name='product_detail_update'),
    path('download-label/', views.download_label, name='download_label'),
    path('create_xcel/<slug:slug>/',
         views.CreateDownloadXcelDoc.as_view(), name='download_doc'),
    path('product/detail/<int:pk>/label_form/',
         views.ProductCreateLabelForm.as_view(), name='get_label_form'),
]
