from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q

import json
import stripe
from google import genai

# Modellerimiz ve Formlarımız
from .models import Product, Category, StockNotification
from .forms import ReviewForm, ProductForm # ProductForm'u ekledik

stripe.api_key = settings.STRIPE_SECRET_KEY

# ==========================================
# ANA SAYFA VE ÜRÜN VİTRİNİ
# ==========================================
def home_view(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')

    products = Product.objects.filter(stock__gt=0).order_by('-created_at')
    categories = Category.objects.all()

    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)

    recently_viewed_ids = request.session.get('recently_viewed', [])
    recently_viewed_products = Product.objects.filter(id__in=recently_viewed_ids)

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'category_slug': category_slug,
        'recently_viewed_products': recently_viewed_products,
    }
    return render(request, 'home.html', context)

def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.all().order_by('-created_at')

    # Session Hafızası İşlemleri
    recently_viewed = request.session.get('recently_viewed', [])
    
    if pk not in recently_viewed:
        recently_viewed.insert(0, pk)
        if len(recently_viewed) > 4:
            recently_viewed.pop()
            
    request.session['recently_viewed'] = recently_viewed

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

# ==========================================
# STOK BİLDİRİMİ VE YAPAY ZEKA
# ==========================================
@login_required
def notify_me_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.stock == 0:
        StockNotification.objects.get_or_create(user=request.user, product=product)
    return redirect('product_detail', pk=pk)

@csrf_exempt 
def ai_assistant_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get('message')

            available_products = Product.objects.filter(stock__gt=0).values_list('title', 'price')
            product_list_text = ", ".join([f"{p[0]} ({p[1]} TL)" for p in available_products])

            system_instruction = f"""Sen bu e-ticaret sitesinin arkadaş canlısı ve profesyonel müşteri asistanısın. 
            Amacın müşterilere kısa ve net cevaplar vererek satış yapmalarını sağlamak. 
            Şu an elimizdeki stokta bulunan ürünler ve fiyatları şunlar: {product_list_text}. 
            Müşteri bir şey sorarsa SADECE bu ürünler üzerinden tavsiye ver. 
            Eğer ilgisiz bir şey sorulursa kibarca e-ticaret asistanı olduğunu hatırlat."""

            # Güncel google-genai kütüphanesine uygun API çağrısı
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            prompt = f"{system_instruction}\n\nMüşteri: {user_message}\nAsistan:"
            
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )

            return JsonResponse({'reply': response.text})
            
        except Exception as e:
            return JsonResponse({'reply': 'Üzgünüm, şu an bağlantı kuramıyorum. Lütfen daha sonra tekrar deneyin.'})
            
    return JsonResponse({'error': 'Geçersiz istek.'}, status=400)


# ==========================================
# ADIM 2: SATICI (VENDOR) FONKSİYONLARI (BİRLEŞTİRİLDİ)
# ==========================================
@login_required(login_url='/accounts/login/')
def vendor_dashboard(request):
    # 1. Satıcının mevcut ürünlerini çek
    my_products = Product.objects.filter(vendor=request.user).order_by('-created_at')
    
    # 2. Yeni ürün ekleme formu (POST işlemi)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_product = form.save(commit=False)
            new_product.vendor = request.user 
            new_product.save()
            # Form gönderildikten sonra sayfayı yenile ki ürün listeye düşsün
            return redirect('vendor_dashboard')
    else:
        # Sayfa ilk açıldığında boş form gönder
        form = ProductForm()
        
    context = {
        'my_products': my_products, # Senin HTML'de kullandığın değişken adı
        'form': form
    }
    return render(request, 'vendor_dashboard.html', context)