# chatbot/views/views.py
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from chatbot.models import CustomUser  # Changed from User to CustomUser

def index(request):
    return render(request, 'chatbot/index.html')

def register_user(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        password = request.POST.get('password')
        
        try:
            # Create user with hashed password
            CustomUser.objects.create_user(uid=uid, password=password)
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('register')
    
    return render(request, 'chatbot/register.html')

def user_login(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        password = request.POST.get('password')
        
        # Authenticate with hashed password
        user = authenticate(request, uid=uid, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid UID or password')
            return redirect('login')
    
    return render(request, 'chatbot/login.html')

def chat(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        # Add your chatbot logic here
        bot_response = "This is a sample response"  # Replace with actual response
        return JsonResponse({'response': bot_response})
    return render(request, 'chatbot/chat.html')

from chatbot.utils import generate_sample_text, text_to_pdf  # Add this import
from django.conf import settings

# chatbot/views/views.py
from django.http import FileResponse
# chatbot/views/views.py
def generate_pdf(request):
    # Generate PDF and redirect to preview
    sample_text = generate_sample_text()
    pdf_filename = text_to_pdf(sample_text)
    return redirect('pdf_preview')

def pdf_preview(request):
    try:
        pdf_files = sorted(
            [f for f in os.listdir(settings.MEDIA_ROOT) if f.endswith('.pdf')],
            key=lambda x: os.path.getctime(os.path.join(settings.MEDIA_ROOT, x)),
            reverse=True
        )
        
        if pdf_files:
            latest_pdf = pdf_files[0]
            pdf_url = f"{settings.MEDIA_URL}{latest_pdf}"
            return render(request, 'chatbot/pdf_preview.html', {
                'pdf_url': pdf_url,
                'pdf_filename': latest_pdf
            })
            
        return render(request, 'chatbot/pdf_preview.html', {'error': 'No reports found'})
    
    except FileNotFoundError:
        return render(request, 'chatbot/pdf_preview.html', {'error': 'Report directory missing'})