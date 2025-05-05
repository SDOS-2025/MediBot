# chatbot/views/views.py
import os
import random
import datetime
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from chatbot.models import CustomUser, DoctorProfile, Treatment
from django.db import IntegrityError
from reports.models import Report
from chatbot.utils import generate_sample_text, text_to_pdf
from django.conf import settings
from django.utils.timezone import now
import logging  # Add logging import

# Add the speech-to-text imports
import uuid
import tempfile
from django.views.decorators.csrf import csrf_exempt
from chatbot.speech_to_text import transcribe_audio

logger = logging.getLogger(__name__)  # Add logger instance


def index(request):
    # Add a link to admin if user is not logged in or not staff/superuser
    show_admin_link = not request.user.is_authenticated or \
                      (request.user.is_authenticated and not request.user.is_staff and not request.user.is_superuser)
    
    context = {
        'show_admin_link': show_admin_link
    }
    
    # Check if the user is authenticated and has a doctor profile
    if request.user.is_authenticated:
        try:
            # This will raise DoctorProfile.DoesNotExist if the profile doesn't exist
            doctor_profile = request.user.doctor_profile
            context['is_doctor'] = True
        except Exception:
            # User doesn't have a doctor profile
            context['is_doctor'] = False
    
    return render(request, 'chatbot/index.html', context)

def register_user(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        age = request.POST.get('age')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        try:
            # Create user with additional fields
            user = CustomUser.objects.create_user(
                uid=uid,
                password=password,
                full_name=full_name,
                age=age,
                email=email,
                phone=phone,
                address=address,
                is_staff=False
            )
            messages.success(request, 'Registration successful! Please login.')
            return redirect('login')
        except IntegrityError as e:
            if 'email' in str(e):
                messages.error(request, 'This email is already registered')
            elif 'uid' in str(e):
                messages.error(request, f'Registration failed: UID "{uid}" already exists.')
            else:
                messages.error(request, 'Registration failed due to existing account information')
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
        age = request.POST.get('age')          # Add this line
        address = request.POST.get('address')  # Add this line
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
                phone=phone,
                age=age,              # Add this
                address=address,      # Add this
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
    doctor_profile = getattr(request.user, 'doctor_profile', None)
    if not doctor_profile:
        return redirect('login')
     # Get doctor's actual specialization from their profile
    doctor_specialization = doctor_profile.specialization
    # Treatments must match both doctor AND reqd=their specialization
    open_treatments = Treatment.objects.filter(
        doctor=request.user,
        is_closed=False,
        reqd=doctor_specialization  # Critical filter
    )
    # Ensure only doctors can access this view
    is_doctor = False
    try:
        if hasattr(request.user, 'doctor_profile') and request.user.doctor_profile is not None:
            is_doctor = True
    except Exception:
        pass
    
    if not is_doctor and not (request.user.is_staff and not request.user.is_superuser):
        messages.error(request, 'Access denied')
        return redirect('login')

    # Only show treatments with required specialization matching the doctor's specialization
    doctor_specialization = request.user.doctor_profile.specialization
    open_treatments = Treatment.objects.filter(
        doctor=request.user,
        is_closed=False,
        reqd=doctor_specialization
    ).select_related('patient').prefetch_related('treatment_reports')

    closed_treatments = Treatment.objects.filter(
        doctor=request.user,
        is_closed=True,
        reqd=doctor_specialization
    ).select_related('patient').prefetch_related('treatment_reports')

    # Get statistics
    today_appointments = Treatment.objects.filter(
        doctor=request.user,
        created_at__date=now().date(),
        reqd=doctor_specialization
    ).count()

    total_patients = Treatment.objects.filter(
        doctor=request.user,
        reqd=doctor_specialization
    ).values('patient').distinct().count()

    total_reports = Report.objects.filter(
        treatment__doctor=request.user,
        treatment__reqd=doctor_specialization
    ).count()

    pending_reviews = Treatment.objects.filter(
        doctor=request.user,
        is_closed=False,
        reqd=doctor_specialization
    ).count()

    context = {
        'open_treatments': open_treatments,
        'closed_treatments': closed_treatments,
        'today_appointments': today_appointments,
        'total_patients': total_patients,
        'total_reports': total_reports,
        'pending_reviews': pending_reviews,
        'recent_reports': Report.objects.filter(
            treatment__doctor=request.user,
            treatment__reqd=doctor_specialization
        ).select_related('user', 'treatment').order_by('-created_at')[:5]
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

@login_required
def view_treatment_history(request, treatment_id):
    # Only assigned doctor with matching specialization can view the history
    treatment = get_object_or_404(Treatment, id=treatment_id, doctor=request.user)
    if treatment.reqd != request.user.doctor_profile.specialization:
        return HttpResponse('Unauthorized: Specialization mismatch', status=403)
    # Build file path
    history_file = os.path.join(settings.MEDIA_ROOT, 'reports_text', f"{treatment.patient.uid}.txt")
    if not os.path.exists(history_file):
        return HttpResponse('No history available for this patient.', status=404)
    with open(history_file, 'r', encoding='utf-8') as f:
        content = f.read()
    # Return as preformatted text
    return HttpResponse(f'<pre style="white-space: pre-wrap;">{content}</pre>')

def chat(request):
    return render(request, 'chatbot/medical_chat.html')

def generate_pdf(request):
    # Only patients generate PDFs
    print(request)
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

def reportgen(request):
    if request.method == 'POST':
        if not request.user.is_authenticated or hasattr(request.user, 'doctor_profile') or request.user.is_superuser:
            return JsonResponse({'status': 'error', 'response': 'Unauthorized'}, status=403)

        user_input = request.POST.get('user_input', '').strip()
        # Prepare directory for storing history files
        import os, datetime
        from django.conf import settings

        history_dir = os.path.join(settings.MEDIA_ROOT, 'reports_text')
        os.makedirs(history_dir, exist_ok=True)
        user_file = os.path.join(history_dir, f"{request.user.uid}.txt")

        # Read existing history
        previous_history = ''
        if os.path.exists(user_file):
            with open(user_file, 'r', encoding='utf-8') as f:
                previous_history = f.read().strip()

        # Build prompt for model including history
        if previous_history:
            prompt = previous_history + "\nUser: " + user_input
        else:
            prompt = user_input

        # Generate response
        try:
            from chatbot.utils import generate_response
            bot_response = generate_response(prompt)
        except Exception as e:
            return JsonResponse({'status': 'error', 'response': 'Error processing request: ' + str(e)})

        # Append interaction to history
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n=== {timestamp} ===\nUser: {user_input}\nBot: {bot_response}\n"
        with open(user_file, 'a', encoding='utf-8') as f:
            f.write(entry)
            print("SXXXXXX")
        print("Datsa addded to file")

        # Create a treatment entry for doctor's review
        from chatbot.models import CustomUser, Treatment
        import random
        doctors = CustomUser.objects.filter(doctor_profile__isnull=False)
        if doctors.exists():
            assigned = random.choice(list(doctors))
            Treatment.objects.create(
                patient=request.user,
                doctor=assigned,
                reqd=assigned.doctor_profile.specialization if assigned.doctor_profile else ''
            )

        return JsonResponse({'status': 'success', 'response': bot_response})

    # GET request - render chat interface
    from django.shortcuts import render
    return render(request, 'chatbot/report_gen.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from google import genai
from google.genai import types
import google.generativeai as genai
genai.configure(api_key="AIzaSyB0R26JpwnrxR1iHP7SRdlXImYhG2NAYLQ")

# Create client instances for different purposes
med_chat_model = genai.GenerativeModel('gemini-2.0-flash')
report_model = genai.GenerativeModel('gemini-2.0-flash')
# system_instruction = (
#     "You are a medical assistant chatbot. Follow this EXACT process:"
#     "\n1. Ask the patient: 'What are your main symptoms?'"
#     "\n2. Ask the patient: 'How long have you been experiencing these symptoms?'"
#     "\n3. Ask the patient: 'Do you have any previous medical conditions?'"
#     "\n4. Based on all previous answers, ask ONE relevant follow-up question."
#     "\n5. Based on all previous answers, ask ONE final relevant follow-up question."
#     "\nAfter collecting all answers, generate a medical report with sections for History of Present Illness, "
#     "Medications, and Allergies. Then include the delimiter '###1234###' on a new line, followed by your preliminary diagnosis."
#     "\nDo NOT ask multiple questions at once. Ask EXACTLY ONE question at a time and wait for the answer."
#     "First old prompt is giiven to u if user has that will be used to generate the report. in complete info explasin that too like earlier issues and then add full info of the user and then ask the question. "
# )

TRANSLATED_QUESTIONS = {
    'en-US': [
        "What are your main symptoms?",
        "How long have you been experiencing these symptoms?",
        "Do you have any previous medical conditions?"
    ],
    'hi-IN': [
        "आपके मुख्य लक्षण क्या हैं?",
        "आपको ये लक्षण कितने समय से हैं?",
        "क्या आपको कोई पूर्व चिकित्सीय स्थितियां हैं?"
    ],
    'bn-IN': [
        "আপনার প্রধান উপসর্গ কী?",
        "আপনি কতদিন ধরে এই উপসর্গগুলি অনুভব করছেন?",
        "আপনার কি কোনো পূর্ববর্তী চিকিৎসা অবস্থা আছে?"
    ],
    'mr-IN': [
        "आपली मुख्य लक्षणे कोणती आहेत?",
        "आपण ही लक्षणे किती दिवसांपासून अनुभवत आहात?",
        "आपल्याला कोणतीही पूर्व वैद्यकीय स्थिती आहे का?"
    ],
    'ta-IN': [
        "உங்கள் முக்கிய அறிகுறிகள் என்ன?",
        "இந்த அறிகுறிகள் எவ்வளவு நாட்களாக உள்ளன?",
        "உங்களுக்கு ஏதேனும் முன் மருத்துவ நிலைகள் உள்ளனவா?"
    ],
    'te-IN': [
        "మీ ప్రధాన లక్షణాలు ఏమిటి?",
        "ఈ లక్షణాలు ఎంతకాలంగా ఉన్నాయి?",
        "మీకు ఎలాంటి గత వైద్య పరిస్థితులు ఉన్నాయా?"
    ],
    'gu-IN': [
        "તમારા મુખ્ય લક્ષણો શું છે?",
        "આ લક્ષણો કેટલા સમયથી છે?",
        "શું તમને કોઈ અગાઉની તબીબી સ્થિતિ છે?"
    ],
    'kn-IN': [
        "ನಿಮ್ಮ ಮುಖ್ಯ ಲಕ್ಷಣಗಳು ಯಾವುವು?",
        "ಈ ಲಕ್ಷಣಗಳು ಎಷ್ಟು ದಿನಗಳಿಂದ ಇವೆ?",
        "ನಿಮಗೆ ಯಾವುದೇ ಹಿಂದಿನ ವೈದ್ಯಕೀಯ ಸ್ಥಿತಿಗಳು ಇದೆಯೆ?"
    ],
    'ml-IN': [
        "നിങ്ങളുടെ പ്രധാന ലക്ഷണങ്ങൾ എന്താണ്?",
        "ഈ ലക്ഷണങ്ങൾ എത്ര ദിവസമായി ഉണ്ട്?",
        "നിങ്ങൾക്ക് മുൻപ് ഏതെങ്കിലും മെഡിക്കൽ അവസ്ഥയുണ്ടോ?"
    ],
    'pa-IN': [
        "ਤੁਹਾਡੇ ਮੁੱਖ ਲੱਛਣ ਕੀ ਹਨ?",
        "ਤੁਸੀਂ ਇਹ ਲੱਛਣ ਕਿੰਨੇ ਸਮੇਂ ਤੋਂ ਮਹਿਸੂਸ ਕਰ ਰਹੇ ਹੋ?",
        "ਕੀ ਤੁਹਾਨੂੰ ਕੋਈ ਪਿਛਲੀ ਮੈਡੀਕਲ ਹਾਲਤ ਹੈ?"
    ],
    'es-ES': [
        "¿Cuáles son sus síntomas principales?",
        "¿Cuánto tiempo ha estado experimentando estos síntomas?",
        "¿Tiene alguna condición médica previa?"
    ],
    'fr-FR': [
        "Quels sont vos principaux symptômes?",
        "Depuis combien de temps avez-vous ces symptômes?",
        "Avez-vous des antécédents médicaux?"
    ]
}

LANGUAGE_MAP = {
    'en-US': 'English',
    'hi-IN': 'Hindi',
    'bn-IN': 'Bengali',
    'mr-IN': 'Marathi',
    'ta-IN': 'Tamil',
    'te-IN': 'Telugu',
    'gu-IN': 'Gujarati',
    'kn-IN': 'Kannada',
    'ml-IN': 'Malayalam',
    'pa-IN': 'Punjabi',
    'es-ES': 'Spanish',
    'fr-FR': 'French'
}

fixed_questions = TRANSLATED_QUESTIONS['en-US']  # Default to English

@csrf_exempt
def medical_chat(request):
    # Get selected language
    selected_lang = request.POST.get('language', request.GET.get('language', 'en-US'))
    lang_name = LANGUAGE_MAP.get(selected_lang, 'English')
    fixed_questions = TRANSLATED_QUESTIONS.get(selected_lang, TRANSLATED_QUESTIONS['en-US'])
    
    # Store language in session
    request.session['selected_lang'] = selected_lang
    
    # System instruction with language context
    system_instruction = (
        f"You are a {lang_name}-speaking medical assistant. Follow these rules:\n"
        "1. Ask questions ONLY in {lang_name}\n"
        "2. Never repeat questions\n"
        "3. Understand inputs in ANY language\n"
        "4. Progress through: symptoms -> duration -> history -> follow-ups\n"
        "5. Make questions distinct and clinically relevant\n\n"
        "Process:\n"
        "1-3: Fixed questions\n4-7: Unique follow-ups\n"
        "After 7 answers, generate report with diagnosis after ###1234###"
    ).format(lang_name=lang_name)
    med_chat_model = genai.GenerativeModel(
        'gemini-1.5-flash',
        system_instruction=system_instruction  # Add this line
    )
    history_dir = os.path.join(settings.MEDIA_ROOT, 'reports_text')
    os.makedirs(history_dir, exist_ok=True)
    history_file = os.path.join(history_dir, f"{request.user.uid}.txt")

    # Initialize or reset session on DELETE
    if request.method == 'DELETE':
        request.session.pop('chat_session', None)
        return JsonResponse({'status': 'reset'})

    # Load or initialize session data
    session = request.session.get('chat_session', {
        'answers': [],
        'question_count': 0,
        'asked_questions': [],  # Track all questions that have been asked
        'initial_prompt': request.POST.get('initial_prompt', '').strip() if request.method == 'POST' else ''
    })

    # Handle GET: start or resume
    if request.method == 'GET':
        # Send first question if no answers yet
        q_idx = session['question_count']
        if q_idx < len(fixed_questions):
            question = fixed_questions[q_idx]
        elif q_idx < len(fixed_questions) + 4:  # Up to 4 follow-up questions
            question = _generate_followup(session['answers'],request)
            
            # Check if this question is too similar to previously asked questions
            if question in session.get('asked_questions', []):
                # Try one more time with a stronger instruction
                question = _generate_followup(session['answers'] + ["Please ask about something different"],request)
        else:
            question = "All questions answered. Please submit your answers to generate the report."
            
        # Track this question
        if 'asked_questions' not in session:
            session['asked_questions'] = []
        if question not in session['asked_questions']:
            session['asked_questions'].append(question)
            
        request.session['chat_session'] = session
        return JsonResponse({'status': 'question', 'question': question})

    # Handle POST: user submitted an answer
    user_input = request.POST.get('user_input', '').strip()
    
    # Get the current question being answered
    q_idx = session['question_count']
    current_question = ""
    if q_idx < len(fixed_questions):
        current_question = fixed_questions[q_idx]
    elif q_idx < len(fixed_questions) + 4 and 'asked_questions' in session and len(session['asked_questions']) > q_idx:
        current_question = session['asked_questions'][q_idx]
    
    # Append user answer to file history with the question it answers
    with open(history_file, 'a', encoding='utf-8') as f:
        f.write(f"Q{session['question_count'] + 1}: {current_question}\nA{session['question_count'] + 1}: {user_input}\n\n")

    # Update session
    session['answers'].append(user_input)
    session['question_count'] += 1
    request.session['chat_session'] = session

    # Decide next step
    q_idx = session['question_count']
    # Next fixed question
    if q_idx < len(fixed_questions):
        next_q = fixed_questions[q_idx]
        return JsonResponse({'status': 'question', 'question': next_q})
    # Four dynamic follow-ups
    elif q_idx < len(fixed_questions) + 4:
        next_q = _generate_followup(session['answers'],request)
        
        # Check if this question is too similar to previously asked questions
        if next_q in session.get('asked_questions', []):
            # Try one more time with a stronger instruction
            next_q = _generate_followup(session['answers'] + ["Please ask about something different"],request)
            
        # Add to asked questions
        if 'asked_questions' not in session:
            session['asked_questions'] = []
        if next_q not in session['asked_questions']:
            session['asked_questions'].append(next_q)
        request.session['chat_session'] = session
        
        return JsonResponse({'status': 'question', 'question': next_q})
    # All 7 questions done, generate report
    else:
        full_history = _compile_history(session['initial_prompt'], session['answers'], session.get('asked_questions', []))
        report, diagnosis, specialization = _generate_report(full_history, request)  # Changed here
        # Write report & diagnosis to file

        # After generating report, diagnosis, specialization = _generate_report(...)
        # Get doctors with the recommended specialization
        doctors = CustomUser.objects.filter(
            doctor_profile__specialization=specialization,
            doctor_profile__isnull=False  # Ensure they have a doctor profile
        )

        # Fallback logic if no specialists found
        if not doctors.exists():
            doctors = CustomUser.objects.filter(
                doctor_profile__specialization='General Medicine',
                doctor_profile__isnull=False
            )

        # Final fallback (assign any available doctor)
        if not doctors.exists():
            doctors = CustomUser.objects.filter(doctor_profile__isnull=False)

        # Assign random doctor from filtered list
        assigned = random.choice(list(doctors)) if doctors.exists() else None

        if assigned:
            Treatment.objects.create(
                patient=request.user,
                doctor=assigned,
                reqd=specialization,  # Set to AI-recommended specialization
                is_closed=False
            )
        else:
            # Handle error (no doctors available)
            pass




        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(f"=== {timestamp} ===\nReport:\n{report}\nDiagnosis: {diagnosis}\nRecommended Specialization: {specialization}\n")  # Changed here
        # Create treatment entry
        doctors = CustomUser.objects.filter(doctor_profile__isnull=False)
        if doctors:
            assigned = random.choice(doctors)
            Treatment.objects.create(
                patient=request.user,
                doctor=assigned,
                reqd=assigned.doctor_profile.specialization or '',
                is_closed=False
            )
        # Clear session
        request.session.pop('chat_session', None)
        return JsonResponse({'status': 'complete', 'report': report, 'diagnosis': diagnosis, 'specialization': specialization})

# Modified _generate_followup function
def _generate_followup(answers, request):
    selected_lang = request.session.get('selected_lang', 'en-US')
    lang_name = LANGUAGE_MAP.get(selected_lang, 'English')
    session = request.session.get('chat_session', {})
    
    # Get previous questions and answers
    asked_questions = session.get('asked_questions', [])
    previous_qa = list(zip(asked_questions, answers))
    
    # Build avoidance context
    avoid_words = {
        'en-US': ["already asked", "repeat", "same"],
        'hi-IN': ["पहले पूछा", "दोहराएं", "वही"],
        'es-ES': ["ya preguntado", "repetir", "mismo"],
        'fr-FR': ["déjà demandé", "répéter", "même"]
    }.get(selected_lang, [])
    
    prompt = (
        f"Generate unique follow-up question in {lang_name} based on:\n"
        "Conversation History:\n" + "\n".join([f"Q{i+1}: {q}\nA{i+1}: {a}" 
                                             for i, (q, a) in enumerate(previous_qa)]) + "\n\n"
        "Rules:\n"
        "1. Ask ONE new question in {lang_name}\n"
        "2. Avoid repeating: {avoid_list}\n"
        "3. Progress diagnosis logically\n"
        "4. Consider: {recent_answers}\n\n"
        "Suggested question:".format(
            lang_name=lang_name,
            avoid_list=", ".join(avoid_words + session.get('asked_questions', [])[-2:]),
            recent_answers=", ".join(answers[-2:])
        )
    )
    
    # Generate with higher temperature for variety
    response = med_chat_model.generate_content(
        prompt,
        generation_config={"temperature": 0.8, "top_p": 0.95}
    )
    question = response.text.strip()
    
    # Add question tracking by topic
    current_topics = _extract_topics(question, selected_lang)
    session['topics'] = session.get('topics', []) + current_topics
    request.session['chat_session'] = session
    
    return question

def _extract_topics(question, lang):
    topic_map = {
        'en-US': {'fever': ['fever', 'temperature', 'thermometer'],
                 'pain': ['pain', 'hurt', 'ache']},
        'hi-IN': {'fever': ['बुखार', 'तापमान', 'थर्मामीटर'],
                 'pain': ['दर्द', 'पीड़ा']},
        # Add other languages
    }
    lang_topics = topic_map.get(lang, topic_map['en-US'])
    return [topic for topic, keywords in lang_topics.items()
           if any(kw in question.lower() for kw in keywords)]
def _compile_history(initial_prompt, answers, asked_questions=None):
    """
    Compile the initial prompt (if any) and patient answers into a single text blob.
    """
    history = []
    if initial_prompt:
        history.append(f"Old Prompt: {initial_prompt}")
    
    # If we have a list of asked questions, use those
    if asked_questions and len(asked_questions) >= len(answers):
        for idx, (question, ans) in enumerate(zip(asked_questions, answers), start=1):
            history.append(f"Q{idx}: {question}")
            history.append(f"A{idx}: {ans}")
    else:
        # Fall back to original behavior
        for idx, ans in enumerate(answers, start=1):
            q = fixed_questions[idx-1] if idx <= len(fixed_questions) else f"Follow-up {idx - len(fixed_questions)}"
            history.append(f"Q{idx}: {q}")
            history.append(f"A{idx}: {ans}")
    
    return "\n".join(history)

def _generate_report(history_text, request):
    """
    Send the full history to GenAI to generate the medical report and diagnosis.
    Only allows specializations from the predefined list.
    """
    # Define allowed specializations from the form
    allowed_specializations = [
        "Cardiology", "Dermatology", "Neurology", "Orthopedics",
        "Pediatrics", "Psychiatry", "General Medicine", "Other"
    ]
    
    prompt = (
        "Generate medical report in English with these sections:\n"
        "1. History of Present Illness\n"
        "2. Medications\n3. Allergies\n"
        "Followed by '###1234###' and diagnosis in English.\n"
        "Then add '###SPECIALIZATION###' followed by ONE recommended doctor specialization "
        "from this exact list: {specializations}. If unsure, choose General Medicine.\n\n"
        "Patient history (may contain multilingual input):\n{history_text}"
    ).format(
        specializations=", ".join(allowed_specializations),
        history_text=history_text
    )
    
    response = report_model.generate_content(
        prompt,
        generation_config={"temperature": 0.3}
    )
    full = response.text.strip()

    report, _, rest = full.partition('###1234###')
    diagnosis, _, specialization = rest.partition('###SPECIALIZATION###')
    
    # Clean and validate specialization
    specialization = specialization.strip()
    if specialization not in allowed_specializations:
        specialization = "General Medicine"  # Default if invalid
    
    return report.strip(), diagnosis.strip(), specialization


@csrf_exempt
def speech_to_text(request):
    """
    API endpoint to handle speech-to-text conversion.
    
    Expects audio data in a POST request, saves it temporarily,
    processes it with SpeechRecognition, and returns the transcribed text.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    try:
        # Check if the request has files
        if not request.FILES or 'audio' not in request.FILES:
            logger.error("No audio file provided in request")
            return JsonResponse({'error': 'No audio file provided'}, status=400)
        
        audio_file = request.FILES['audio']
        
        logger.info(f"Received audio file: {audio_file.name}, size: {audio_file.size} bytes, content_type: {audio_file.content_type}")
        
        # Create a temporary file to store the audio
        file_extension = os.path.splitext(audio_file.name)[1] if '.' in audio_file.name else '.wav'
        temp_file = tempfile.NamedTemporaryFile(suffix=file_extension, delete=False)
        
        # Save uploaded file to the temporary file
        try:
            for chunk in audio_file.chunks():
                temp_file.write(chunk)
            temp_file.close()
            logger.info(f"Audio saved to temporary file: {temp_file.name}")
        except Exception as e:
            logger.error(f"Error saving audio file: {e}", exc_info=True)
            return JsonResponse({'error': 'Error saving audio file'}, status=500)
        
        # Process the audio file with SpeechRecognition
        try:
            transcribed_text = transcribe_audio(temp_file.name)
            logger.info(f"Transcription result: {transcribed_text}")
            
            # Check if the response contains an error message
            if (
                "error" in transcribed_text.lower() or 
                "could not understand" in transcribed_text.lower() or
                "unavailable" in transcribed_text.lower()
            ):
                return JsonResponse({'error': transcribed_text})
                
            return JsonResponse({'text': transcribed_text})
        except Exception as e:
            logger.error(f"Error in transcription process: {e}", exc_info=True)
            return JsonResponse({'error': 'Failed to transcribe audio'}, status=500)
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file.name)
                logger.debug(f"Temporary file {temp_file.name} deleted")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_file.name}: {e}")
    
    except Exception as e:
        logger.error(f"Unexpected error in speech_to_text view: {e}", exc_info=True)
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)