from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'), # type: ignore
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('download_invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
    path('cancel_order/<int:order_id>', views.cancel_order, name='cancel_order'),
    path('cash_on_delivery', views.cash_on_delivery, name='cash_on_delivery'),
    path('cod_invoice/<int:order_id>', views.cod_invoice, name='cod_invoice'), 
]
