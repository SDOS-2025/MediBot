# chatbot/views/views.py
import os
import random
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from chatbot.models import CustomUser, DoctorProfile, Treatment
from django.db import IntegrityError
from reports.models import Report
from chatbot.utils import generate_sample_text, text_to_pdf
from django.conf import settings


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
    # Ensure only doctors can access this view
    if not hasattr(request.user, 'doctor_profile'):
        messages.error(request, 'Access denied')
        return redirect('login')

    # Fetch open and closed treatments assigned to the logged-in doctor
    open_treatments = Treatment.objects.filter(doctor=request.user, is_closed=False)
    closed_treatments = Treatment.objects.filter(doctor=request.user, is_closed=True)

    context = {
        'open_treatments': open_treatments,
        'closed_treatments': closed_treatments,
    }
    return render(request, 'chatbot/doctor_dashboard.html', context)

@login_required
def close_treatment(request, treatment_id):
    # Fetch the treatment and ensure it belongs to the logged-in doctor
    treatment = get_object_or_404(Treatment, id=treatment_id, doctor=request.user)
    treatment.is_closed = True
    treatment.save()

    messages.success(request, f'Treatment for patient {treatment.patient.uid} has been closed.')
    return redirect('doctor_dashboard')

def chat(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        bot_response = "This is a sample response"  # Replace with actual chatbot logic
        return JsonResponse({'response': bot_response})
    
    if not request.user.is_authenticated or request.user.is_staff or request.user.is_superuser:
        messages.warning(request, 'Please log in as a patient to use the chat.')
        return redirect('login')
        
    return render(request, 'chatbot/chat.html')

def generate_pdf(request):
    # Only patients generate PDFs
    if not request.user.is_authenticated or hasattr(request.user, 'doctor_profile') or request.user.is_superuser:
        messages.error(request, 'Only patients can generate reports.')
        return redirect('login')

    # Pick a random doctor with matching specialty requirement
    doctors = CustomUser.objects.filter(doctor_profile__isnull=False)
    if not doctors.exists():
        messages.error(request, 'No doctors available to assign.')
        return redirect('index')
    assigned = random.choice(list(doctors))
    specialty = assigned.doctor_profile.specialization
    # Look for existing open treatment for this patient and specialty
    treatment = Treatment.objects.filter(
        patient=request.user,
        doctor=assigned,
        is_closed=False,
        reqd=specialty
    ).first()
    if not treatment:
        treatment = Treatment.objects.create(
            patient=request.user,
            doctor=assigned,
            reqd=specialty
        )

    # Generate PDF file on disk
    dummy_text = f"Patient Report for {request.user.uid}"  # placeholder text
    filename = text_to_pdf(dummy_text)
    filepath = os.path.join(settings.MEDIA_ROOT, filename)

    # Read PDF as blob
    with open(filepath, 'rb') as f:
        pdf_data = f.read()

    # Save report in database with PDF blob
    report = Report.objects.create(
        title=f"Report_{treatment.id}",
        content=dummy_text,
        user=request.user,
        assigned_doctor=assigned,
        treatment=treatment,
        pdf_blob=pdf_data
    )

    # Stream PDF back to the browser
    return FileResponse(BytesIO(pdf_data), content_type='application/pdf', as_attachment=True, filename=filename)

def pdf_preview(request):
    # Preview a PDF stored in MEDIA folder via ?file=filename.pdf
    file_name = request.GET.get('file')
    if not file_name:
        messages.error(request, 'No file specified for preview.')
        return redirect('index')
    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
    if not os.path.exists(file_path):
        messages.error(request, 'Requested file does not exist.')
        return redirect('index')
    return FileResponse(open(file_path, 'rb'), content_type='application/pdf')

from django.http import JsonResponse
from chatbot.utils import generate_response  # Import your AI model function

def report_gen(request):
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        
        try:
            # Get response from your AI model
            bot_response = generate_response(user_input)
            return JsonResponse({
                'response': bot_response,
                'status': 'success'
            })
        except Exception as e:
            return JsonResponse({
                'response': 'Error processing request: ' + str(e),
                'status': 'error'
            })
    
    # GET request - render chat interface
    return render(request, 'chatbot/report_gen.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyB0R26JpwnrxR1iHP7SRdlXImYhG2NAYLQ")

system_instruction = (
    "You are a medical assistant chatbot. Follow this EXACT process:"
    "\n1. Ask the patient: 'What are your main symptoms?'"
    "\n2. Ask the patient: 'How long have you been experiencing these symptoms?'"
    "\n3. Ask the patient: 'Do you have any previous medical conditions?'"
    "\n4. Based on all previous answers, ask ONE relevant follow-up question."
    "\n5. Based on all previous answers, ask ONE final relevant follow-up question."
    "\nAfter collecting all answers, generate a medical report with sections for History of Present Illness, "
    "Medications, and Allergies. Then include the delimiter '###1234###' on a new line, followed by your preliminary diagnosis."
    "\nDo NOT ask multiple questions at once. Ask EXACTLY ONE question at a time and wait for the answer."
)
fixed_questions = [
    "What are your main symptoms?",
    "How long have you been experiencing these symptoms?",
    "Do you have any previous medical conditions?"
]
@csrf_exempt
def medical_chat(request):
    if request.method == 'DELETE':
        request.session.pop('chat_session', None)
        return JsonResponse({'status': 'reset'})
    
    # Initialize session data
    chat_session = request.session.get('chat_session')

    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        
        try:
            # Initialize or retrieve chat session
            if not chat_session:
                # Create new chat session
                chat = client.chats.create(
                    model="gemini-1.5-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )
                # Store initial session data
                chat_session = {
                    'history': [],
                    'question_count': 0
                }
            else:
                # Rebuild chat from history with proper Part formatting
                chat = client.chats.create(
                    model="gemini-1.5-flash",
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    ),
                    history=[{
                        'role': msg['role'], 
                        'parts': [types.Part(text=part) for part in msg['parts']]
                    } for msg in chat_session['history']]
                )

            # Send user input as properly formatted Part
            response = chat.send_message(types.Part(text=user_input))
            bot_response = response.text.strip()
            
            # Update session data with text strings
            chat_session['history'].extend([
                {'role': 'user', 'parts': [user_input]},
                {'role': 'model', 'parts': [bot_response]}
            ])
            chat_session['question_count'] += 1
            request.session['chat_session'] = chat_session
            
            # Determine next step based on question count
            if chat_session['question_count'] < 3:
                next_q = fixed_questions[chat_session['question_count']]
                return JsonResponse({'status': 'question', 'question': next_q})
            elif chat_session['question_count'] == 3:
                response = chat.send_message(types.Part(text="Based on the previous answers, ask ONE relevant follow-up question."))
                return JsonResponse({'status': 'question', 'question': response.text.strip()})
            elif chat_session['question_count'] == 4:
                response = chat.send_message(types.Part(text="Based on all previous answers, ask ONE final relevant follow-up question."))
                return JsonResponse({'status': 'question', 'question': response.text.strip()})
            else:
                # Generate final report
                response = chat.send_message(types.Part(text="Generate the medical report with delimiter as instructed."))
                report, _, diagnosis = response.text.partition('###1234###')
                request.session.pop('chat_session', None)
                return JsonResponse({
                    'status': 'complete',
                    'report': report.strip(),
                    'diagnosis': diagnosis.strip()
                })
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    else:  # GET request
        if not chat_session:
            return JsonResponse({'status': 'question', 'question': fixed_questions[0]})
        
        last_message = next((msg for msg in reversed(chat_session['history']) 
                          if msg['role'] == 'model'), None)
        return JsonResponse({'status': 'question', 'question': last_message['parts'][0]})