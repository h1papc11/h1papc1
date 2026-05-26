from django.contrib import admin
from django.urls import path, include
from django.conf import settings # <-- Düzeltilen satır burası
from django.conf.urls.static import static
from products.views import home_view, vendor_dashboard

urlpatterns = [
    path('h1papc1.1.1.1/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('orders.urls')),
    path('chat/', include('chat.urls')),
    path('admin/', admin.site.urls),
    path('dashboard/', vendor_dashboard, name='vendor_dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)