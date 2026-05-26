from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required # YENİ EKLENDİ
from .forms import CustomUserCreationForm
from products.models import Product
from products.forms import ProductForm

# --- GİRİŞ VE ÇIKIŞ İŞLEMLERİ ---
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # AKILLI YÖNLENDİRME (YENİ EKLENDİ)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'vendor':
                return redirect('vendor_dashboard')
            else:
                return redirect('customer_dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

# --- ÖZEL PANELLER (YENİ EKLENDİ) ---
# @login_required, misafirlerin URL yazarak bu sayfalara girmesini engeller.

@login_required
def customer_dashboard(request):
    return render(request, 'customer_dashboard.html')

@login_required
def vendor_dashboard(request):
    # Ekstra Güvenlik: Sadece "Satıcı" rolündekiler bu sayfayı kullanabilsin
    if request.user.role != 'vendor':
        return redirect('home')
    
    # Eğer ürün ekle butonuna basıldıysa
    if request.method == 'POST':
        # request.FILES görsel veya dosya yükleme işlemleri için zorunludur!
        form = ProductForm(request.POST, request.FILES) 
        if form.is_valid():
            # commit=False: Ürünü oluştur ama hemen veritabanına kaydetme, bekle!
            product = form.save(commit=False) 
            # Ürünün satıcısı, o an formu dolduran kişidir
            product.vendor = request.user 
            product.save() # Şimdi kaydet
            form.save_m2m() # Kategoriler (Many-to-Many) için bunu ayrıca kaydetmek zorundayız
            
            return redirect('vendor_dashboard') # Sayfayı yenile
    else:
        # Sayfaya normal giriş yapıldıysa boş form göster
        form = ProductForm()

    # Sadece bu satıcıya ait (giriş yapan kişiye ait) ürünleri veritabanından çek
    my_products = Product.objects.filter(vendor=request.user)

    return render(request, 'vendor_dashboard.html', {'form': form, 'my_products': my_products})
@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

def register_view(request):
    # Eğer formu doldurup gönderdiyse (POST)
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() # Kullanıcıyı veritabanına kaydet
            login(request, user) # Kayıt olduktan sonra otomatik giriş yaptır
            
            # Kayıt olan kişinin rolüne göre onu yönlendir
            if user.role == 'vendor':
                return redirect('vendor_dashboard')
            else:
                return redirect('customer_dashboard')
    else:
        # Sayfaya ilk defa giriyorsa boş form göster (GET)
        form = CustomUserCreationForm()
        
    return render(request, 'register.html', {'form': form})

# --- GEÇİCİ ADMİN OLUŞTURMA KODU ---
from django.contrib.auth import get_user_model
try:
    User = get_user_model()
    if not User.objects.filter(username='supercreater').exists():
        User.objects.create_superuser(
            username='h1papc1', 
            email='umut-karali-53@hotmail.com', 
            password='karali53'
        )
        print("Admin kullanıcısı başarıyla oluşturuldu!")
except Exception as e:
    print("Admin oluşturulurken hata veya zaten var:", e)
# ----------------------------------