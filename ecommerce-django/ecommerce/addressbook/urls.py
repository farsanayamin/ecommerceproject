from django.urls import path
from . import views

urlpatterns = [
    path('activate/<int:address_id>', views.activate, name='activate'),
    path('add_address/', views.add_address, name='add_address'),
    path('edit_address/<int:address_id>', views.edit_address, name='edit_address' )
]
