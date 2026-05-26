from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Rolleri belirliyoruz
    ROLE_CHOICES = (
        ('customer', 'Müşteri'),
        ('vendor', 'Satıcı'),
        ('admin', 'Admin'),
    )
    
    # E-posta ile giriş yapılacağı için benzersiz (unique) yapıyoruz
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    # Django'ya giriş yaparken 'username' yerine 'email' sormasını söylüyoruz
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email