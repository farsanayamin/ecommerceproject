from django.urls import path
from . import views
urlpatterns = [
    path('', views.store, name='store'),
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('brand/<slug:brand_slug>/', views.store, name='products_by_brand'),
    path('product/<slug:brand_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),

    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),

    # Brands
    path('brand_list/', views.brand_list, name='brand_list'),

    # Categories
    path('category_list/', views.category_list, name='category_list'),

    # filter
    path('filter_data', views.filter_data, name='filter_data'),


]
