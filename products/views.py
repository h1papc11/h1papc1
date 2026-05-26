
from .models import Product
from django.shortcuts import render, get_object_or_404, redirect
from .forms import ReviewForm
import stripe
from django.conf import settings
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from google import genai
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

@csrf_exempt # Geçici olarak AJAX isteklerinde kolaylık sağlaması için
def ai_assistant_view(request):
    if request.method == "POST":
        try:
            # Gelen mesajı oku
            data = json.loads(request.body)
            user_message = data.get('message')

            # Gemini API'sini çalıştır
            genai.configure(api_key=settings.GEMINI_API_KEY)

            # 1. Veritabanından stoktaki ürünleri alıyoruz
            available_products = Product.objects.filter(stock__gt=0).values_list('title', 'price')
            
            # 2. Ürünleri yapay zekanın okuyabileceği bir metne çeviriyoruz
            product_list_text = ", ".join([f"{p[0]} ({p[1]} TL)" for p in available_products])

            # 3. Sisteme kim olduğunu öğretiyoruz (Sistem Promptu)
            system_instruction = f"""Sen bu e-ticaret sitesinin arkadaş canlısı ve profesyonel müşteri asistanısın. 
            Amacın müşterilere kısa ve net cevaplar vererek satış yapmalarını sağlamak. 
            Şu an elimizdeki stokta bulunan ürünler ve fiyatları şunlar: {product_list_text}. 
            Müşteri bir şey sorarsa SADECE bu ürünler üzerinden tavsiye ver. 
            Eğer ilgisiz bir şey sorulursa kibarca e-ticaret asistanı olduğunu hatırlat."""

            # 4. Modeli başlat ve cevabı üret
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"{system_instruction}\n\nMüşteri: {user_message}\nAsistan:"
            
            response = model.generate_content(prompt)

            # Cevabı siteye (arayüze) geri gönder
            return JsonResponse({'reply': response.text})
            
        except Exception as e:
            return JsonResponse({'reply': 'Üzgünüm, şu an bağlantı kuramıyorum. Lütfen daha sonra tekrar deneyin.'})
            
    return JsonResponse({'error': 'Geçersiz istek.'}, status=400)