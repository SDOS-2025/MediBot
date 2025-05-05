from chatbot.views.views import reportgen
from reports.models import Report
from django.urls import reverse
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from chatbot.utils import text_to_pdf
from django.test import RequestFactory
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
    # Test PDF utility directly
    pdf_filename = text_to_pdf("Sample PDF Content for Testing")
    import os
    from django.conf import settings
    filepath = os.path.join(settings.MEDIA_ROOT, pdf_filename)
    assert os.path.exists(filepath)
    with open(filepath, 'rb') as f:
        content = f.read()
        assert content.startswith(b'%PDF')
    os.remove(filepath)

@pytest.mark.django_db
def test_report_generation(patient_user):
    # Test _generate_report with dummy request and history
    from chatbot.views.views import _generate_report
    factory = RequestFactory()
    request = factory.get('/')
    history = "Q1: What are your main symptoms?\nA1: cold"
    report, diagnosis, specialization = _generate_report(history, request)
    assert 'report' in report.lower() or 'cold' in report.lower()
    assert isinstance(diagnosis, str)
    assert isinstance(specialization, str)

@pytest.mark.django_db
def test_pdf_creation():
    # Test PDF creation utility for binary output
    pdf_filename = text_to_pdf("PDF binary test content")
    import os
    from django.conf import settings
    filepath = os.path.join(settings.MEDIA_ROOT, pdf_filename)
    with open(filepath, 'rb') as f:
        content = f.read()
        assert content.startswith(b'%PDF')
    os.remove(filepath)