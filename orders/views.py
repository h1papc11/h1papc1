from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
import stripe

from products.models import Product
from .models import Cart, CartItem, Coupon

# Stripe Gizli Anahtarımızı ayarlıyoruz
stripe.api_key = settings.STRIPE_SECRET_KEY

# ==========================================
# 1. SEPETE ÜRÜN EKLEME
# ==========================================
@login_required(login_url='/accounts/login/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    # Ürün zaten sepette varsa adetini artır
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        
    messages.success(request, f"{product.title} başarıyla sepetinize eklendi.")
    return redirect('cart_view')

# ==========================================
# 2. SEPETİ GÖRÜNTÜLEME VE KUPON HESAPLAMA
# ==========================================
@login_required(login_url='/accounts/login/')
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    
    # Alt Toplam (İndirimsiz ham tutar)
    sub_total = sum(item.get_total_price() for item in items)
    total_amount = sub_total
    discount_amount = 0
    
    # Eğer sepette aktif bir kupon varsa yeni toplamı hesapla
    if cart.coupon and cart.coupon.is_active:
        discount_amount = (sub_total * cart.coupon.discount_percent) / 100
        total_amount = sub_total - discount_amount
    
    context = {
        'cart': cart, 
        'items': items, 
        'sub_total': sub_total,
        'total_amount': total_amount,
        'discount_amount': discount_amount
    }
    return render(request, 'cart.html', context)

# ==========================================
# 3. KUPON UYGULAMA
# ==========================================
@login_required(login_url='/accounts/login/')
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        try:
            # Kodu veritabanında ara ve aktif mi kontrol et
            coupon = Coupon.objects.get(code=code, is_active=True)
            cart = Cart.objects.get(user=request.user)
            cart.coupon = coupon
            cart.save()
            messages.success(request, f"Harika! %{coupon.discount_percent} indirim uygulandı.")
        except Coupon.DoesNotExist:
            messages.error(request, "Geçersiz veya süresi dolmuş bir kupon kodu girdiniz.")
            
    return redirect('cart_view')

# ==========================================
# 4. STRIPE İLE GÜVENLİ ÖDEME (CHECKOUT)
# ==========================================
@login_required(login_url='/accounts/login/')
def create_checkout_session(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.all()
    
    if not items:
        messages.warning(request, "Sepetiniz boş, ödeme yapabilmek için ürün eklemelisiniz.")
        return redirect('cart_view')

    # Toplam tutarı hesapla
    sub_total = sum(item.get_total_price() for item in items)
    total_amount = sub_total
    
    if cart.coupon and cart.coupon.is_active:
        discount = (sub_total * cart.coupon.discount_percent) / 100
        total_amount = sub_total - discount
        
    # Stripe tam sayı (integer) ister. 100 ile çarparak kuruşa çeviriyoruz.
    stripe_total = int(total_amount * 100)
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'try', # Türk Lirası
                    'product_data': {
                        'name': f"{request.user.username} Siparişi",
                    },
                    'unit_amount': stripe_total,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('payment_success')),
            cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
        )
        return redirect(session.url, code=303)
    except Exception as e:
        messages.error(request, f"Ödeme sistemi başlatılamadı: {str(e)}")
        return redirect('cart_view')

# ==========================================
# 5. BAŞARILI / BAŞARISIZ ÖDEME EKRANLARI
# ==========================================
@login_required(login_url='/accounts/login/')
def payment_success(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    # Ödeme başarılıysa müşterinin sepetindeki ürünleri sil ve kuponu kaldır
    cart.items.all().delete()
    cart.coupon = None
    cart.save()
    
    return render(request, 'payment_success.html')

@login_required(login_url='/accounts/login/')
def payment_cancel(request):
    return render(request, 'payment_cancel.html')