# chatbot/views/views.py
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