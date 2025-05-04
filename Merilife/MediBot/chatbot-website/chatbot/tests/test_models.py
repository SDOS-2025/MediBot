from django.test import TestCase
from chatbot.models import CustomUser, DoctorProfile, PatientProfile, Treatment
from django.core.exceptions import ValidationError

class UserModelTests(TestCase):
    def test_create_patient_user(self):
        user = CustomUser.objects.create_user(
            uid='patient123',
            password='testpass123',
            full_name='John Doe',
            email='john@example.com',
            phone='1234567890',
            age=30,
            address='123 Main St'
        )
        self.assertEqual(user.is_staff, False)
        self.assertEqual(user.full_name, 'John Doe')
        
    def test_create_doctor_user(self):
        user = CustomUser.objects.create_user(
            uid='dr_smith',
            password='testpass123',
            full_name='Dr. Smith',
            email='smith@example.com',
            phone='0987654321',
            age=45,
            address='456 Clinic Rd',
            is_staff=True
        )
        DoctorProfile.objects.create(
            user=user,
            specialization='Cardiology',
            qualification='MD'
        )
        self.assertTrue(hasattr(user, 'doctor_profile'))
        self.assertEqual(user.doctor_profile.specialization, 'Cardiology')

    def test_patient_profile_creation(self):
        user = CustomUser.objects.create_user(
            uid='patient456',
            password='testpass123',
            full_name='Jane Doe',
            email='jane@example.com',
            phone='5551234567',
            age=25,
            address='789 Oak St'
        )
        PatientProfile.objects.create(
            user=user,
            blood_group='O+',
            height=170,
            weight=65
        )
        self.assertEqual(user.patient_profile.blood_group, 'O+')

class TreatmentModelTests(TestCase):
    def setUp(self):
        self.doctor = CustomUser.objects.create_user(
            uid='dr_jones',
            password='testpass123',
            full_name='Dr. Jones',
            email='jones@example.com',
            phone='1112223333',
            age=50,
            address='789 Hospital Rd',
            is_staff=True
        )
        self.patient = CustomUser.objects.create_user(
            uid='patient789',
            password='testpass123',
            full_name='Mike Johnson',
            email='mike@example.com',
            phone='4445556666',
            age=35,
            address='321 Pine St'
        )
        DoctorProfile.objects.create(user=self.doctor, specialization='Neurology')

    def test_treatment_creation(self):
        treatment = Treatment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis='Migraine',
            prescribed_medication='Ibuprofen'
        )
        self.assertEqual(treatment.diagnosis, 'Migraine')
        self.assertFalse(treatment.is_closed)