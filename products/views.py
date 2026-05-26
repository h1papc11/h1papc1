
from .models import Product
from django.shortcuts import render, get_object_or_404, redirect
from .forms import ReviewForm
import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


def home_view(request):
    # Vitrindeki tüm ürünler
    products = Product.objects.all()
    
    # Hafızadaki gezilen ürün ID'lerini al
    recently_viewed_ids = request.session.get('recently_viewed', [])
    
    # Bu ID'lere sahip olan ürünleri veritabanından getir (id__in komutu bu işe yarar)
    recently_viewed_products = Product.objects.filter(id__in=recently_viewed_ids)
    
    return render(request, 'home.html', {
        'products': products,
        'recently_viewed_products': recently_viewed_products
    })
def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all().order_by('-created_at')

    # --- YENİ: Session Hafızası İşlemleri ---
    # Kullanıcının hafızasındaki 'recently_viewed' listesini al, yoksa boş liste döndür
    recently_viewed = request.session.get('recently_viewed', [])
    
    # Eğer bu ürünün ID'si listede yoksa, listenin en başına (index 0) ekle
    if pk not in recently_viewed:
        recently_viewed.insert(0, pk)
        # Hafıza şişmesin diye sadece son 4 ürünü tut
        if len(recently_viewed) > 4:
            recently_viewed.pop()
            
    # Güncel listeyi tekrar hafızaya (Session) kaydet
    request.session['recently_viewed'] = recently_viewed
    # ----------------------------------------

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                return redirect('product_detail', pk=pk)
    else:
        form = ReviewForm()

    return render(request, 'product_detail.html', {
        'product': product, 
        'reviews': reviews, 
        'form': form
    })

from django.contrib.auth.decorators import login_required
from .models import Product, StockNotification # StockNotification import edildi

# ... (mevcut kodlar) ...

@login_required
def notify_me_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Sadece stoğu biten ürünler için bekleme listesine eklenebilir
    if product.stock == 0:
        # Kullanıcı zaten listede yoksa ekler, varsa hata vermez
        StockNotification.objects.get_or_create(user=request.user, product=product)
        
    return redirect('product_detail', pk=pk)