from chatbot.views.views import reportgen
from reports.models import Report
from django.urls import reverse
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from chatbot.views.views import _generate_report as generate_report, generate_pdf
# Update tests to use reportgen response
def test_report_content_generation(patient_user):
    client = Client()
    client.force_login(patient_user)
    response = client.post(reverse('reportgen'), {'user_input': 'cold'})
    assert response.status_code == 200
    assert 'Upper Respiratory Infection' in response.json()['response']

def test_pdf_generation(sample_report):
    """Test PDF formatting"""
    pdf = generate_pdf(sample_report)
    assert b'%PDF' in pdf[:4]  # PDF magic number

def test_report_generation(patient_user):
    report = generate_report(patient_user)
    assert 'URI' in report.content
    assert report.patient == patient_user

def test_pdf_creation(sample_report):
    pdf_content = generate_pdf(sample_report)
    assert pdf_content.startswith(b'%PDF')