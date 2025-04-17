# chatbot/views/views.py
import os
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from chatbot.models import CustomUser, DoctorProfile  # add DoctorProfile
from django.db import IntegrityError  # Import IntegrityError
from reports.models import Report  # add import at top

def index(request):
    # Add a link to admin if user is not logged in or not staff/superuser
    show_admin_link = not request.user.is_authenticated or \
                      (request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser)
    context = {
        'show_admin_link': show_admin_link
    }
    return render(request, 'chatbot/index.html', context)

def register_user(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        password = request.POST.get('password')
        
        try:
            # Create a regular user
            CustomUser.objects.create_user(uid=uid, password=password, is_staff=False)
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        except IntegrityError:  # Catch duplicate UID for regular users too
            messages.error(request, f'Registration failed: UID "{uid}" already exists.')
            return redirect('register')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            return redirect('register')
    
    return render(request, 'chatbot/register.html')

def user_login(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        password = request.POST.get('password')
        user = authenticate(request, uid=uid, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin:index')
            # doctors are users with a linked DoctorProfile
            if hasattr(user, 'doctor_profile'):
                return redirect('doctor_dashboard')
            # regular users
            return redirect('index')
        else:
            messages.error(request, 'Invalid UID or password')
            return render(request, 'chatbot/login.html', {'uid': uid})
    return render(request, 'chatbot/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
@user_passes_test(lambda u: u.is_superuser)  # Only superusers (admins) can access this view
def register_doctor(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        specialization = request.POST.get('specialization')
        qualification = request.POST.get('qualification')
        bio = request.POST.get('bio')
        
        try:
            # Create a regular user (doctor) without admin rights
            doctor_user = CustomUser.objects.create_user(
                uid=uid,
                password=password,
                is_staff=False,
                full_name=full_name,
                email=email,
                phone=phone
            )
            # Create associated DoctorProfile
            DoctorProfile.objects.create(
                user=doctor_user,
                specialization=specialization,
                qualification=qualification,
                bio=bio
            )
            messages.success(request, f'Dr. {full_name or uid} registered successfully!')
            return redirect('register_doctor')
        except IntegrityError:  # Catch the duplicate UID error
            messages.error(request, f'Failed to register doctor: UID "{uid}" already exists.')
            return redirect('register_doctor')
        except Exception as e:
            messages.error(request, f'Failed to register doctor: {str(e)}')
            return redirect('register_doctor')
    
    return render(request, 'chatbot/register_doctor.html')

@login_required
def doctor_dashboard(request):
    # only users with a DoctorProfile should access
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'You do not have access to the doctor dashboard.')
        return redirect('login')
    # Fetch reports assigned to this doctor
    patients_reports = Report.objects.filter(assigned_doctor=request.user)
    context = {
        'patients_reports': patients_reports,
    }
    return render(request, 'chatbot/doctor_dashboard.html', context)

def chat(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        bot_response = "This is a sample response"  # Replace with actual chatbot logic
        return JsonResponse({'response': bot_response})
    
    if not request.user.is_authenticated or request.user.is_staff or request.user.is_superuser:
        messages.warning(request, 'Please log in as a patient to use the chat.')
        return redirect('login')
        
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