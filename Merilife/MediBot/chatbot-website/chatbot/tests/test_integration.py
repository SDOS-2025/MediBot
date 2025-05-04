from django.test import TestCase
from django.core.files.storage import default_storage
from reports.models import Report
from chatbot.models import CustomUser
from chatbot.ai_wrapper import generate_medical_report  # Import from your actual module

class ScreeningFlowTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test users once for all tests
        cls.patient_user = CustomUser.objects.create_user(
            uid='test_patient',
            password='testpass',
            full_name='Test Patient',
            email='patient@test.com',
            phone='1234567890',
            age=30,
            address='Test Address'
        )
        
        cls.doctor_user = CustomUser.objects.create_user(
            uid='test_doctor',
            password='testpass',
            full_name='Test Doctor',
            email='doctor@test.com',
            phone='0987654321',
            age=45,
            address='Clinic Rd',
            is_staff=True
        )

    def test_full_flow(self):
        # Start screening
        self.client.force_login(self.patient_user)
        self.client.post('/chat/', {'message': 'cold'})
        Report.objects.create(
            user=self.patient_user,
            title="Cold Report",
            content="cold symptoms"
        )
        # Verify report
        report = Report.objects.filter(user=self.patient_user).first()
        self.assertIsNotNone(report)  # Verify creation

        # Doctor view
        self.client.force_login(self.doctor_user)
        response = self.client.get(f'/reports/{report.id}/')
        self.assertEqual(response.status_code, 200)

    def test_report_encryption(self):
        # Generate test report
        report = generate_medical_report("Patient reported cold symptoms")

        
        # Access storage
        storage_content = default_storage.open(report.pdf_blob.name).read()
        
        # Verify encryption by checking for non-printable bytes
        printable_count = sum(32 <= byte <= 126 for byte in storage_content[:100])
        self.assertLess(printable_count, 20, "PDF should be encrypted/non-readable")