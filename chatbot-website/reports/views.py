from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Report
from meditron.utils import generate_response  # Fix import statement
from chatbot.models import CustomUser  # add import
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
            doctors = CustomUser.objects.filter(is_staff=True, specialization=specialty)
        else:
            doctors = CustomUser.objects.filter(is_staff=True)
        if doctors.exists():
            assigned = random.choice(list(doctors))
            report.assigned_doctor = assigned
            report.save()
        return JsonResponse({'status': 'success', 'report_id': report.id})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def view_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    return render(request, 'reports/report_detail.html', {'report': report})