from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    # BAĞLANTILAR
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Satıcı")
    # Çoklu categories yerine yeni arama sistemimiz için tekil category'e geçtik
    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kategori")
    
    # ÜRÜN BİLGİLERİ
    title = models.CharField(max_length=200, verbose_name="Ürün Adı")
    description = models.TextField(verbose_name="Detaylı Açıklama")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stok Miktarı")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Ürün Kapak Görseli")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

    # GÖZLEMCİ (OBSERVER) FONKSİYONU - Stok bildirimleri için
    def save(self, *args, **kwargs):
        # Eğer bu ürün daha önceden veritabanında varsa (yani güncelleniyorsa)
        if self.pk: 
            old_product = Product.objects.get(pk=self.pk)
            # Eğer ürünün eski stoğu 0 ise ve şimdi 0'dan büyük bir değere güncellendiyse
            if old_product.stock == 0 and self.stock > 0:
                from chat.models import Message # Döngüsel içe aktarma hatasını önlemek için
                
                # Bu ürünü bekleyen herkese satıcının ağzından otomatik mesaj at
                for notification in self.waitlist.all():
                    Message.objects.create(
                        sender=self.vendor,
                        receiver=notification.user,
                        subject=f"Müjde! '{self.title}' Tekrar Stokta",
                        body=f"Merhaba, beklediğiniz '{self.title}' ürünü mağazamızda tekrar stoklara girmiştir. Tükenmeden hemen sepetinize ekleyebilirsiniz."
                    )
                    # Mesaj gönderildikten sonra kullanıcıyı bekleme listesinden çıkar
                    notification.delete()
                    
        super().save(*args, **kwargs) # Ürünün normal kaydetme işlemini tamamla

class StockNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='waitlist')

    def __str__(self):
        return f"{self.user.username} -> {self.product.title} Bekliyor"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/", verbose_name="Ürün Görseli")

    def __str__(self):
        return f"{self.product.title} Görseli"
    
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        verbose_name="Puan (1-5)"
    )
    comment = models.TextField(verbose_name="Yorum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yorum Tarihi")

    def __str__(self):
        return f"{self.user.username} - {self.product.title} - {self.rating} Yıldız"