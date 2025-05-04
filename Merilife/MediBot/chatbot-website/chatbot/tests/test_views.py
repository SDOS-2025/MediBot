from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from chatbot.models import CustomUser, DoctorProfile
# from chatbot.factories import UserFactory, DoctorProfileFactory  # Ensure you have these factories

class AuthViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            uid='testuser',
            password='Testpass123!',
            full_name='Test User',
            email='test@example.com',
            phone='1234567890',
            age=30,
            address='Test Address'
        )

    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'uid': 'testuser',
            'password': 'Testpass123!'
        })
        self.assertRedirects(response, reverse('index'))

    def test_registration_view(self):
        response = self.client.post(reverse('register'), {
            'uid': 'newuser',
            'password': 'Newpass123!',
            'full_name': 'New User',
            'email': 'new@example.com',
            'phone': '0987654321',
            'age': 25,
            'address': 'New Address'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CustomUser.objects.filter(uid='newuser').exists())

class DoctorDashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create doctor user directly
        self.doctor = CustomUser.objects.create_user(
            uid='testdr',
            password='Testpass123!',
            full_name='Test Doctor',
            email='doctor@example.com',
            phone='1112223333',
            age=45,
            address='Clinic Rd',
            is_staff=True
        )
        # Create doctor profile directly
        DoctorProfile.objects.create(
            user=self.doctor,
            specialization='Cardiology',
            qualification='MD',
            bio='Heart specialist'
        )
        self.client.login(uid='testdr', password='Testpass123!')

    def test_dashboard_access(self):
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertContains(response, 'Cardiology')
        self.assertContains(response, 'Test Doctor')
class ChatViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create regular user directly
        self.user = CustomUser.objects.create_user(
            uid='chatuser',
            password='Testpass123!',
            full_name='Chat User',
            email='chat@example.com',
            phone='4445556666',
            age=28,
            address='Chat Address'
        )
        self.client.login(uid='chatuser', password='Testpass123!')

    def test_chat_interface(self):
        response = self.client.get(reverse('medical_chat'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'chat-container')

    def test_chat_submission(self):
        response = self.client.post(reverse('medical_chat'), {
            'message': 'I have a headache'
        }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {"status": "question", "question": "What are your main symptoms?"}
        )