from django.db import models
from django.conf import settings
from products.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator

# ==========================================
# İNDİRİM KUPONU MODELİ
# ==========================================
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Kupon Kodu")
    discount_percent = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], verbose_name="İndirim Yüzdesi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    def __str__(self):
        return f"{self.code} (%{self.discount_percent} İndirim)"

# ==========================================
# MÜŞTERİ SEPETİ MODELİ
# ==========================================
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Uygulanan Kupon")
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        # Sepetteki tüm ürünlerin indirimsiz (ham) toplam tutarını hesaplar
        return sum(item.get_total_price() for item in self.items.all())

    def get_discounted_price(self):
        # Eğer sepette aktif bir kupon varsa, indirimli tutarı hesaplar ve döndürür
        total = self.get_total_price()
        if self.coupon and self.coupon.is_active:
            discount_amount = (total * self.coupon.discount_percent) / 100
            return total - discount_amount
        return total

    def __str__(self):
        return f"{self.user.username} kullanıcısının sepeti"

# ==========================================
# SEPETTEKİ ÜRÜN KALEMLERİ MODELİ
# ==========================================
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Adet")

    def get_total_price(self):
        # Ürünün fiyatı ile sepetteki adet sayısını çarpar
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} adet {self.product.title}"