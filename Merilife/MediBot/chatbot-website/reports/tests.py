from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Report

class ReportModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            uid='testuser',
            full_name="Test User",
            email="test@example.com",
            phone="1234567890",
            age=30,
            address="Test Address"
        )
        self.report = Report.objects.create(
            user=self.user,
            title="Test Report Title",  # Required field
            content="Test report content",
        )

    def test_report_creation(self):
        self.assertEqual(self.report.user.uid, 'testuser')
        self.assertEqual(self.report.content, "Test report content")
        self.assertEqual(self.report.title, "Test Report Title")  # Add this

    def test_string_representation(self):
        expected_str = "Test Report Title"  # Match the title
        self.assertEqual(str(self.report), expected_str)