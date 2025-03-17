from django.test import TestCase
from .models import Report

class ReportModelTest(TestCase):
    def setUp(self):
        self.report = Report.objects.create(
            user_id=1,
            appointment_date='2023-10-01',
            report_content='This is a test report.'
        )

    def test_report_creation(self):
        self.assertEqual(self.report.user_id, 1)
        self.assertEqual(self.report.appointment_date, '2023-10-01')
        self.assertEqual(self.report.report_content, 'This is a test report.')

    def test_string_representation(self):
        self.assertEqual(str(self.report), f'Report for user {self.report.user_id} on {self.report.appointment_date}')