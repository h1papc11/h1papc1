from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def send_message(request, receiver_id):
    # Alıcıyı bul (örneğin satıcı)
    receiver = get_object_or_404(User, id=receiver_id)
    
    if request.method == 'POST':
        subject = request.POST.get('subject')
        body = request.POST.get('body')
        
        # Mesajı veritabanına kaydet
        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            subject=subject,
            body=body
        )
        return redirect('inbox') # Gönderdikten sonra kendi gelen kutuna dön
        
    return render(request, 'send_message.html', {'receiver': receiver})

@login_required
def inbox(request):
    # Bana gelen tüm mesajları tarihe göre (en yeni en üstte) sırala
    messages = request.user.received_messages.all().order_by('-created_at')
    return render(request, 'inbox.html', {'messages': messages})