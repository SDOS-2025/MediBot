from django.test import TestCase
from django.urls import reverse
from chatbot.models import CustomUser,DoctorProfile

class AuthTests(TestCase):
    def test_patient_registration(self):
        response = self.client.post(reverse('register'), {
            'uid': 'newpatient',
            'password': 'SecurePass123!',
            'full_name': 'Test Patient',
            'email': 'patient@test.com',
            'phone': '1234567890',
            'age': 30,
            'address': 'Test Address'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(CustomUser.objects.count(), 1)

    def test_doctor_access_control(self):
        doctor = CustomUser.objects.create_user(
            uid='testdoctor',
            password='testpass123',
            full_name='Test Doctor',
            email='doctor@test.com',
            phone='0987654321',
            age=45,
            address='Clinic Rd',
            is_staff=True
        )
        DoctorProfile.objects.create(user=doctor, specialization='Cardiology')
        self.client.login(uid='testdoctor', password='testpass123')
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {
            'uid': 'invalid',
            'password': 'wrong'
        })
        self.assertContains(response, 'Invalid UID or password')