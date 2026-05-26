from django.urls import path
from . import views

urlpatterns = [
    # Sepet Görüntüleme Ana Sayfası (Örn: /orders/)
    path('', views.cart_view, name='cart_view'),
    
    # Sepete Ürün Ekleme
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    
    # İndirim Kuponu Uygulama
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    
    # Stripe Ödeme Döngüsü (Payment Loop)
    path('checkout/', views.create_checkout_session, name='checkout'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
]