from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Cart, CartItem
from .models import Cart, CartItem, Coupon # Coupon eklendi
from django.contrib import messages
import stripe
from django.conf import settings
from django.urls import reverse
@login_required
def add_to_cart(request, product_id):
    # Eklenmek istenen ürünü bul
    product = get_object_or_404(Product, id=product_id)
    
    # Giriş yapan kullanıcının sepetini bul (Yoksa yeni bir tane oluşturur)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Bu ürün kullanıcının sepetinde zaten var mı kontrol et
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    # Eğer ürün zaten sepette varsa sadece miktarını (adetini) 1 artır
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
        
    # İşlem bitince kullanıcıyı sepet sayfasına yönlendir
    return redirect('cart_view')

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    
    # Sepetteki tüm ürünlerin (birim fiyat * adet) toplamını hesapla
    total_amount = sum(item.get_total_price() for item in items)
    
    return render(request, 'cart.html', {'cart': cart, 'items': items, 'total_amount': total_amount})

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code')
        try:
            # Kodu veritabanında ara ve aktif mi diye bak
            coupon = Coupon.objects.get(code=code, is_active=True)
            cart = Cart.objects.get(user=request.user)
            cart.coupon = coupon
            cart.save()
        except Coupon.DoesNotExist:
            # Kupon bulunamazsa veya pasifse
            pass # İleride buraya hata mesajı ekleyebiliriz
            
    return redirect('cart_view')

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    
    # Alt Toplam (İndirimsiz)
    sub_total = sum(item.get_total_price() for item in items)
    total_amount = sub_total
    discount_amount = 0
    
    # Eğer sepette kupon varsa, yeni toplamı hesapla
    if cart.coupon:
        discount_amount = (sub_total * cart.coupon.discount_percent) / 100
        total_amount = sub_total - discount_amount
    
    return render(request, 'cart.html', {
        'cart': cart, 
        'items': items, 
        'sub_total': sub_total,
        'total_amount': total_amount,
        'discount_amount': discount_amount
    })

@login_required
def create_checkout_session(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.all()
    
    # Toplam tutarı kuruş/cent cinsinden hesaplıyoruz (Stripe tam sayı ister)
    sub_total = sum(item.get_total_price() for item in items)
    total_amount = sub_total
    
    if cart.coupon:
        discount = (sub_total * cart.coupon.discount_percent) / 100
        total_amount = sub_total - discount
        
    # Stripe için tutarı 100 ile çarpıp tam sayıya (integer) çeviriyoruz (Örn: 50.50 TL -> 5050 kuruş)
    stripe_total = int(total_amount * 100)
    
    # Stripe Ödeme Oturumu (Checkout Session) Oluşturma
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
        # Ödeme başarılı olursa veya iptal edilirse yönlendirilecek URL'ler
        success_url=request.build_absolute_uri(reverse('payment_success')),
        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
    )
    
    # Kullanıcıyı güvenli Stripe ödeme sayfasına yönlendir
    return redirect(session.url, code=303)

@login_required
def payment_success(request):
    # Ödeme başarılıysa kullanıcının sepetini boşalt
    cart = get_object_or_404(Cart, user=request.user)
    cart.items.all().delete()
    cart.coupon = None
    cart.save()
    return render(request, 'payment_success.html')

@login_required
def payment_cancel(request):
    return render(request, 'payment_cancel.html')