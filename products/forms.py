from django import forms
from .models import Product, Review

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # Satıcıyı (vendor) formdan çıkardık çünkü arka planda otomatik ekleyeceğiz.
        fields = ['categories', 'title', 'description', 'price', 'stock']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        # Kullanıcıdan sadece puan ve yorum metnini istiyoruz
        fields = ['rating', 'comment']