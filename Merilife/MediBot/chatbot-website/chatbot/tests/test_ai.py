from django.test import TestCase
from chatbot.ai_wrapper import send_chat_message, generate_medical_report
from unittest.mock import patch
from unittest.mock import MagicMock

class AITests(TestCase):
    @patch('chatbot.ai_wrapper.GENAI_CLIENT_WORKING', False)
    def test_fallback_response(self):
        response = send_chat_message('hello')
        self.assertIn('Hello! I\'m your medical assistant', response)
    
    @patch('chatbot.ai_wrapper.GENAI_AVAILABLE', True)
    @patch('chatbot.ai_wrapper.GENAI_CLIENT_WORKING', True)
    @patch('chatbot.ai_wrapper.client')
    def test_genai_integration(self, mock_client):
        mock_chat = MagicMock()
        mock_response = MagicMock()
        mock_response.text = 'Mocked AI response'
        mock_chat.send_message.return_value = mock_response
        mock_client.chats.create.return_value = mock_chat
        response = send_chat_message('test message')
        self.assertEqual(response, 'Mocked AI response')

    def test_medical_report_generation(self):
        with patch('chatbot.ai_wrapper.GENAI_CLIENT_WORKING', False):
            report = generate_medical_report('Patient has fever')
            self.assertIn('MEDICAL REPORT', report)