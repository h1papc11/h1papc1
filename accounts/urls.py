from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'), # YENİ EKLENDİ
    
    path('customer/', views.customer_dashboard, name='customer_dashboard'),
    path('vendor/', views.vendor_dashboard, name='vendor_dashboard'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    
]