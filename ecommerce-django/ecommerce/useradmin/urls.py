from django.urls import path
from . import views
urlpatterns = [
    path('', views.useradmin, name='useradmin'),
    path('unauthorized/', views.decorator, name='decorator'),

#===========================Users==================================
# Customers----------------------------------------------------------------------------------------------------
    path('customers/', views.customers, name='customers'),
    path('block_user/<int:user_id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:user_id>/', views.unblock_user, name='unblock_user'),

#Admin-------------------------------------------------------------------------------------------------------- 
    path('admin_list/', views.admin_list, name='admin_list' ),
    path('delete_admin/<int:user_id>/', views.delete_admin, name='delete_admin'),
    path('create_admin/', views.create_admin, name='create_admin'),

# Categories----------------------------------------------------------------------------------------------------
    path('categories/', views.categories, name='categories'),
    path('edit_category/<int:cat_id>', views.edit_category, name='edit_category'),
    path('delete_category/<int:cat_id>', views.delete_category, name='delete_category'),
    path('add_category', views.add_category, name='add_category'),

# Brands-------------------------------------------------------------------------------------------------------------
    path('brands/', views.brands, name='brands'),
    path('edit_brand/<int:brand_id>', views.edit_brand, name='edit_brand'),
    path('delete_brand/<int:brand_id>', views.delete_brand, name='delete_brand'),
    path('add_brand', views.add_brand, name='add_brand'),

# Products------------------------------------------------------------------------------------------------------------
    path('products/', views.products, name='products'),
    path('edit_product/<int:product_id>', views.edit_product, name='edit_product'),
    path('delete_image/<int:image_id>', views.delete_image, name='delete_image'),
    path('delete_product/<int:product_id>', views.delete_product, name='delete_product'),
    path('add_product', views.add_product, name='add_product'),

# Product Variations-----------------------------------------------------------------------------------------------------------------
    path('variations', views.variations, name='variations'),
    path('edit_variation/<int:variation_id>', views.edit_variation, name='edit_variation'),
    path('delete_variation/<int:variation_id>', views.delete_variation, name='delete_variation'),
    path('add_variation', views.add_variation, name='add_variation'),
    path('colors_size', views.colors_size, name='colors_size'),
    path('add_size', views.add_size, name='add_size'),
    path('delete_size/<int:size_id>', views.delete_size, name='delete_size'),
    path('add_color', views.add_color, name='add_color'),
    path('delete_color/<int:color_id>', views.delete_color, name='delete_color'),
# Orders------------------------------------------------------------------------------------------------------------------------------
    path('orders', views.orders, name='orders'),
    path('ship/<int:order_id>', views.ship, name='ship'),
    path('order_detail/<int:order_id>', views.order_detail, name='order_detail_table'),
    path('cancelled_orders', views.cancelled_orders, name='cancelled_orders'),
    path('restock/<int:order_id>', views.restock, name='restock'),
    path('new_orders/', views.new_orders, name='new_orders'),

# Product Offer------------------------------------------------------------------------------------------------------------------------

    path('product_offer', views.product_offer, name='product_offer'),
    path('add_product_offer', views.add_product_offer, name='add_product_offer'),
    path('edit_product_offer/<int:product_offer_id>', views.edit_product_offer, name='edit_product_offer'),
    path('delete_product_offer/<int:product_offer_id>', views.delete_product_offer, name='delete_product_offer'),

# Category Offer------------------------------------------------------------------------------------------------------------------------------
    path('category_offer', views.category_offer, name='category_offer'),
    path('add_category_offer', views.add_category_offer, name='add_category_offer'),
    path('edit_category_offer/<int:category_offer_id>', views.edit_category_offer, name='edit_category_offer'),
    path('delete_category_offer/<int:category_offer_id>', views.delete_category_offer, name='delete_category_offer'),

# Coupons ------------------------------------------------------------------------------------------------------------------------------------
    path('coupons', views.coupons, name='coupons'),
    path('add_coupon', views.add_coupon, name='add_coupon'),
    path('edit_coupon/<int:coupon_id>', views.edit_coupon, name='edit_coupon'),
    path('delete_coupon/<int:coupon_id>', views.delete_coupon, name='delete_coupon'),

# Reports
    path('download_sales_report',views.download_sales_report, name='download_sales_report'),

    path('refund_payment/<int:order_id>', views.refund_payment, name='refund')
]

