from django.shortcuts import render
from django.http import JsonResponse
from .utils import generate_response

def index(request):
    return render(request, 'chatbot/index.html')

def chat(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        bot_response = generate_response(user_input)
        return JsonResponse({'response': bot_response})
    return render(request, 'chatbot/chat.html')