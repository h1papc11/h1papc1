from django.db import models
from django.conf import settings

class Message(models.Model):
    # Mesajı gönderen kişi
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages', verbose_name="Gönderen")
    # Mesajı alan kişi
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages', verbose_name="Alıcı")
    
    subject = models.CharField(max_length=200, verbose_name="Konu")
    body = models.TextField(verbose_name="Mesaj İçeriği")
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False, verbose_name="Okundu mu?")

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username} | {self.subject}"