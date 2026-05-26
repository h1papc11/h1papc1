from django.contrib import admin
from .models import Category, Product, ProductImage

# Kategori modelini basitçe kaydediyoruz
admin.site.register(Category)

# Ürün sayfasının içine görselleri entegre eden yapı
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1 # Varsayılan olarak 1 boş görsel yükleme alanı sunar

# Ürün modelini özel ayarlarıyla kaydediyoruz
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'vendor', 'price', 'stock'] # Admin listesinde görünecek sütunlar
    list_filter = ['categories', 'vendor'] # Sağ tarafa filtreleme menüsü ekler
    inlines = [ProductImageInline] # Görsel ekleme alanını ürün sayfasına bağladık

admin.site.register(Product, ProductAdmin)