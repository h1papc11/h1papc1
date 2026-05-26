from django.db import models
from django.conf import settings # Özel kullanıcı modelimize ulaşmak için
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")

    def __str__(self):
        return self.name

class Product(models.Model):
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Satıcı")
    categories = models.ManyToManyField(Category, verbose_name="Kategoriler")
    title = models.CharField(max_length=200, verbose_name="Ürün Adı")
    description = models.TextField(verbose_name="Detaylı Açıklama")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stok Miktarı")
    
    def __str__(self):
        return self.title

    # YENİ EKLENEN GÖZLEMCİ (OBSERVER) FONKSİYONU
    def save(self, *args, **kwargs):
        # Eğer bu ürün daha önceden veritabanında varsa (yani yeni yaratılmıyor, güncelleniyorsa)
        if self.pk: 
            old_product = Product.objects.get(pk=self.pk)
            # Eğer ürünün eski stoğu 0 ise ve şimdi 0'dan büyük bir değere güncellendiyse
            if old_product.stock == 0 and self.stock > 0:
                from chat.models import Message # Döngüsel içe aktarma hatasını önlemek için burada çağırıyoruz
                
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

# YENİ EKLENEN BEKLEME LİSTESİ MODELİ
class StockNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='waitlist')

    def __str__(self):
        return f"{self.user.username} -> {self.product.title} Bekliyor"

class ProductImage(models.Model):
    # Bir ürünün BİRDEN FAZLA görseli olabileceği için ayrı bir tablo kurduk.
    # Bu tabloyu ForeignKey ile Product (Ürün) tablosuna bağladık.
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/", verbose_name="Ürün Görseli")

    def __str__(self):
        return f"{self.product.title} Görseli"
    
class Review(models.Model):
    # Yorumu ürüne bağlıyoruz (related_name ile üründen yorumlara kolayca ulaşacağız)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    # Yorumu yapana bağlıyoruz
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], 
        verbose_name="Puan (1-5)"
    )
    comment = models.TextField(verbose_name="Yorum")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yorum Tarihi")

    def __str__(self):
        return f"{self.user.username} - {self.product.title} - {self.rating} Yıldız"