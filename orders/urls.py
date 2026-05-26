from django.urls import path
from . import views

urlpatterns = [
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    
    # Ödeme Linkleri YENİ EKLENDİ
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    
    path('', views.cart_view, name='cart_view'),
]