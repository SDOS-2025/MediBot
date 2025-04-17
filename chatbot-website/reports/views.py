from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Report
from meditron.utils import generate_response  # Fix import statement
from chatbot.models import CustomUser, Treatment  # add imports
import random  # add random import

def report_view(request):
    if request.method == 'GET':
        reports = Report.objects.all()
        return render(request, 'reports/report.html', {'reports': reports})

def generate_report(request):  # Fix function name
    if request.method == 'POST':
        user_data = request.POST.get('user_data')
        report_content = generate_response(user_data)  # Use correct function
        report = Report(content=report_content, user=request.user)
        report.save()
        # assign random doctor by matching specialization if provided
        specialty = request.POST.get('specialization')
        if specialty:
            doctors = CustomUser.objects.filter(doctor_profile__specialization=specialty)
        else:
            doctors = CustomUser.objects.filter(doctor_profile__isnull=False)
        if doctors.exists():
            assigned = random.choice(list(doctors))
            # reuse existing open treatment or create new one, update reqd if changed
            treatment = Treatment.objects.filter(
                patient=request.user,
                doctor=assigned,
                is_closed=False
            ).first()
            if treatment:
                if specialty and treatment.reqd != specialty:
                    treatment.reqd = specialty
                    treatment.save()
            else:
                treatment = Treatment.objects.create(
                    patient=request.user,
                    doctor=assigned,
                    reqd=specialty
                )
            report.assigned_doctor = assigned
            report.treatment = treatment
            report.save()
        return JsonResponse({'status': 'success', 'report_id': report.id})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def view_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    return render(request, 'reports/report_detail.html', {'report': report})