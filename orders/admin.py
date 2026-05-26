from django.contrib import admin
from .models import Cart, CartItem, Coupon # Coupon eklendi

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Coupon) # Yeni eklendi