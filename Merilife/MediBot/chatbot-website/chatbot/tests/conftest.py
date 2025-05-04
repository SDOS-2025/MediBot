import pytest
pytestmark = pytest.mark.django_db  # Add at top of file
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from chatbot.models import CustomUser, DoctorProfile, PatientProfile, Treatment
from reports.models import Report
import factory
import random
import os

CustomUser = get_user_model()

# ---------------------------
# Factory Boy Implementation
# ---------------------------
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    uid = factory.Sequence(lambda n: f'user_{n}')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    full_name = factory.Faker('name')
    email = factory.Faker('email')
    # phone = factory.Faker('phone_number')
    phone = factory.Faker('numerify', text='##########') 
    age = factory.Faker('random_int', min=18, max=90)
    address = factory.Faker('address')

class DoctorProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DoctorProfile

    specialization = factory.Faker('random_element', elements=['Cardiology', 'Neurology', 'Pediatrics'])
    qualification = factory.Faker('job')
    bio = factory.Faker('text')

class PatientProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PatientProfile

    blood_group = factory.Faker('random_element', elements=['A+', 'B+', 'O+', 'AB+'])
    height = factory.Faker('pyfloat', right_digits=2, positive=True, min_value=150, max_value=200)
    weight = factory.Faker('pyfloat', right_digits=2, positive=True, min_value=40, max_value=150)

# ---------------------------
# Core Fixtures
# ---------------------------
@pytest.fixture
def patient_user():
    user = UserFactory()
    PatientProfileFactory(user=user)
    return user

@pytest.fixture
def doctor_user():
    user = UserFactory(is_staff=True)
    DoctorProfileFactory(user=user)
    return user

@pytest.fixture
def admin_user():
    return UserFactory(
        is_staff=True,
        is_superuser=True,
    )

# In all Report fixtures like sample_report, empty_report, etc:
@pytest.fixture
def sample_report(patient_user):
    return Report.objects.create(
        user=patient_user,
        content="Upper Respiratory Infection (URI)",
        # Remove 'status'
    )

@pytest.fixture
def empty_report(patient_user):
    return Report.objects.create(
        user=patient_user,
        content="",
    )

@pytest.fixture
def invalid_status_report(patient_user):  # Rename this fixture
    return Report.objects.create(
        user=patient_user,
        content="Test Content",
    )

# ---------------------------
# Edge Cases
# ---------------------------
@pytest.fixture
def incomplete_user():
    return UserFactory(
        full_name='',
        email='',
        phone='',
        age=None,
        address=''
    )

@pytest.fixture
def edge_case_user():
    return UserFactory(
        full_name='A' * 255,  # Max length
        email='a' * 50 + '@example.com',
        phone='+' + '1' * 20,
        age=150,
        address='X' * 1000
    )

# ---------------------------
# Report Fixtures
# ---------------------------
@pytest.fixture
def empty_report(patient_user):
    return Report.objects.create(
        user=patient_user,
        content="",
        status='DRAFT'
    )

@pytest.fixture
def invalid_status_report(patient_user):
    return Report.objects.create(
        user=patient_user,
        content="Test Content",
        status='INVALID_STATUS'
    )

# ---------------------------
# Security Fixtures
# ---------------------------
@pytest.fixture
def malicious_user():
    return UserFactory(
        uid="'; DROP TABLE users; --",
        full_name="<script>alert('xss')</script>",
        email="sql@injection.com"
    )

# ---------------------------
# Bulk Data Fixtures
# ---------------------------
@pytest.fixture
def bulk_patients():
    return UserFactory.create_batch(100)

@pytest.fixture
def bulk_reports(bulk_patients):
    reports = []
    for patient in bulk_patients:
        reports.append(Report.objects.create(
            user=patient,
            content=f"Report for {patient.uid}",
            status=random.choice(['PENDING', 'REVIEWED'])
        ))
    return reports

# ---------------------------
# Treatment Fixtures
# ---------------------------
@pytest.fixture
def open_treatment(patient_user, doctor_user):
    return Treatment.objects.create(
        patient=patient_user,
        doctor=doctor_user,
        diagnosis='Migraine',
        prescribed_medication='Ibuprofen'
    )

@pytest.fixture
def closed_treatment(patient_user, doctor_user):
    return Treatment.objects.create(
        patient=patient_user,
        doctor=doctor_user,
        diagnosis='Flu',
        prescribed_medication='Tamiflu',
        is_closed=True
    )

# ---------------------------
# Cleanup Fixtures
# ---------------------------
@pytest.fixture(autouse=True)
def media_cleanup():
    """Clean media files after each test"""
    yield
    # Delete all test media files
    for root, dirs, files in os.walk(default_storage.location):
        for name in files:
            os.remove(os.path.join(root, name))

# ---------------------------
# Parameterized Fixtures
# ---------------------------
@pytest.fixture(params=['PATIENT', 'DOCTOR', 'ADMIN'])
def all_user_types(request):
    user_type = request.param
    if user_type == 'PATIENT':
        user = UserFactory()
        PatientProfileFactory(user=user)
    elif user_type == 'DOCTOR':
        user = UserFactory(is_staff=True)
        DoctorProfileFactory(user=user)
    else:  # ADMIN
        user = UserFactory(is_staff=True, is_superuser=True)
    return user

@pytest.fixture(params=['PENDING', 'REVIEWED', 'ARCHIVED', 'INVALID_STATUS'])
def all_report_statuses(request, patient_user):
    return Report.objects.create(
        user=patient_user,
        content="Test Report",
        status=request.param
    )