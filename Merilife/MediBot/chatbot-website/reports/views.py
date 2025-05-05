from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, FileResponse
from .models import Report
from meditron.utils import generate_response  # Fix import statement
from chatbot.models import CustomUser, Treatment  # add imports
from django.contrib.auth.decorators import login_required
import random  # add random import
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

@login_required
def view_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    
    # Security check - only allow viewing if the user is the patient or the assigned doctor
    if not (request.user == report.user or 
            (hasattr(request.user, 'doctor_profile') and report.treatment and report.treatment.doctor == request.user)):
        return HttpResponse('Unauthorized', status=403)
    
    # Otherwise render the report content as HTML
    return render(request, 'reports/report_detail.html', {'report': report})

@login_required
def download_report_pdf(request, report_id):
    report = get_object_or_404(Report, id=report_id)
    # Only allow assigned doctor to download
    if not (hasattr(request.user, 'doctor_profile') and report.assigned_doctor == request.user):
        return HttpResponse('Unauthorized', status=403)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    # Patient info header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 50, f"Patient Name: {report.user.full_name}")
    c.drawString(50, height - 70, f"Age: {report.user.age}")
    c.drawString(50, height - 90, f"Date: {report.created_at.strftime('%Y-%m-%d %H:%M')}")
    # Report content body
    c.setFont("Helvetica", 12)
    text_object = c.beginText(50, height - 120)
    for line in report.content.splitlines():
        text_object.textLine(line)
    c.drawText(text_object)
    c.showPage()
    c.save()

    buffer.seek(0)
    # Save PDF to blob
    report.pdf_blob = buffer.getvalue()
    report.save(update_fields=['pdf_blob'])

    # Return PDF file response
    return FileResponse(buffer, as_attachment=True, filename=f'report_{report.id}.pdf', content_type='application/pdf')