from django.urls import path
from . import views

urlpatterns = [
    path('<int:pk>/', views.product_detail_view, name='product_detail'),
    path('notify/<int:pk>/', views.notify_me_view, name='notify_me'), # YENİ EKLENDİ
]