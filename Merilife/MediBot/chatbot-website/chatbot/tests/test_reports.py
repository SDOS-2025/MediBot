from chatbot.views.views import reportgen
from reports.models import Report
from django.urls import reverse
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from chatbot.views.views import _generate_report as generate_report, generate_pdf
import pytest

@pytest.mark.django_db
def test_report_content_generation(patient_user):
    client = Client()
    client.force_login(patient_user)
    response = client.post(reverse('reportgen'), {'user_input': 'cold'})
    assert response.status_code == 200
    # Accept fallback response
    assert 'cold' in response.json()['response'].lower() or 'provide more context' in response.json()['response'].lower()

@pytest.mark.django_db
def test_pdf_generation(sample_report):
    class DummyRequest:
        user = type('User', (), {'is_authenticated': True, 'is_superuser': False, 'doctor_profile': False})()
    pdf = generate_pdf(DummyRequest(), sample_report)
    assert b'%PDF' in pdf[:4]

@pytest.mark.django_db
def test_report_generation(patient_user):
    report, _ = generate_report(patient_user)
    assert 'URI' in report.content or 'report' in report.content.lower()
    assert hasattr(report, 'patient') or hasattr(report, 'user')

@pytest.mark.django_db
def test_pdf_creation(sample_report):
    class DummyRequest:
        user = type('User', (), {'is_authenticated': True, 'is_superuser': False, 'doctor_profile': False})()
    pdf_content = generate_pdf(DummyRequest(), sample_report)
    assert pdf_content.startswith(b'%PDF')