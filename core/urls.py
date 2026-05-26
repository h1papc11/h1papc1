from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products.views import home_view, vendor_dashboard

urlpatterns = [
    # Gizli ve güvenli admin panelin
    path('h1papc1.1.1.1/', admin.site.urls),
    
    # Ana Sayfa ve Satıcı Paneli
    path('', home_view, name='home'),
    path('dashboard/', vendor_dashboard, name='vendor_dashboard'),
    
    # 1. YENİ EKLENEN: Django-Allauth Rotaları (Google OAuth vb.)
    # DİKKAT: Bunun senin kendi accounts yolundan ÖNCE gelmesi çok önemlidir.
    path('accounts/', include('allauth.urls')),
    
    # 2. Senin Kendi Uygulamalarının Rotaları
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('orders.urls')),
    path('chat/', include('chat.urls')),
]

# Medya (Resim vb.) dosyalarının yüklenmesi için gerekli ayar
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)