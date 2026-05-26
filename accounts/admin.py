from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Admin listesinde rolü de görmek için list_display'i güncelliyoruz
    list_display = ['email', 'username', 'role', 'is_staff']
    
    # Kullanıcı detay sayfasında 'role' alanını görünür yapmak için fieldsets'e ekliyoruz
    fieldsets = UserAdmin.fieldsets + (
        ('Rol Bilgisi', {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)