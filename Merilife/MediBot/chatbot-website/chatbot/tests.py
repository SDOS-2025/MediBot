from django.test import TestCase
from .models import UserInteraction

class UserInteractionModelTest(TestCase):
    def setUp(self):
        UserInteraction.objects.create(user_input="Hello", bot_response="Hi there!")
    
    def test_user_interaction_creation(self):
        interaction = UserInteraction.objects.get(user_input="Hello")
        self.assertEqual(interaction.bot_response, "Hi there!")

class ChatbotViewTest(TestCase):
    def test_chatbot_response(self):
        response = self.client.post('/chatbot/chat/', {'user_input': 'How can I book an appointment?'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You can book an appointment by...")  # Adjust based on expected response

class ReportGenerationTest(TestCase):
    def test_report_generation(self):
        response = self.client.get('/reports/generate/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Report generated successfully")  # Adjust based on expected output