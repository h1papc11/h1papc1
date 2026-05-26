from django.urls import path
from . import views
from .views import home_view, product_detail_view, ai_assistant_view
urlpatterns = [
    path('<int:pk>/', views.product_detail_view, name='product_detail'),
    path('notify/<int:pk>/', views.notify_me_view, name='notify_me'), # YENİ EKLENDİ
    path('ask-ai/', ai_assistant_view, name='ask_ai'),
]