from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # Kayıt ekranında kullanıcıdan hangi bilgileri isteyeceğimizi seçiyoruz
        fields = ('email', 'username', 'role')