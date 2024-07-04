from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    ###
    path('otpsubmission/verify/<int:id>/', views.otp_verification, name='otp_verification'),
    path('resendotp/<int:id>/',views.resendotp,name='resendotp' ),
    path('forgotPassword/',views.forgotPassword, name='forgotPassword'),
    #path('forgotPassword/otp/<int:id>/', views.otp_verification_forgot,name ='otp_verification_forgot'),
    path('otp_password/<int:id>/<str:otp_verified>/', views.otp_password, name='otp_password'),
    path('reset_password/<int:id>/<str:otp_verified>/', views.reset_password, name='reset_password'),




    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    #path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    #path('reset_password_validate/<uidb64>/<token>', views.reset_password_validate, name='reset_password_validate'),
    #path('resetPassword/', views.resetPassword, name='resetPassword'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('addressbook', views.addressbook, name='addressbook'),

    # Reference code
    path('register/<str:ref_code>/', views.register, name='register'),

   ]
