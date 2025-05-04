from django.test import TestCase
from allpairspy import AllPairs
from django.urls import reverse
from django.contrib.auth import get_user_model

class PairwiseAuthTests(TestCase):
    def test_login_combinations(self):
        # Create test user with all required fields
        CustomUser = get_user_model()
        CustomUser.objects.create_user(
            uid='valid_user',
            password='valid_pass',
            full_name='Test User',
            email='test@example.com',
            phone='1234567890',
            age=30,
            address='Test Address'
        )

        parameters = [
            ["valid_user", "invalid_user"],  # UID
            ["valid_pass", "invalid_pass"],  # Password
            ["mobile", "desktop"]  # Device type
        ]
        
        for combo in AllPairs(parameters):
            uid, pwd, device = combo
            with self.subTest(uid=uid, pwd=pwd, device=device):
                # Simulate device type in headers
                headers = {'HTTP_USER_AGENT': 'Chrome Mobile' if device == 'mobile' else 'Chrome Desktop'}
                
                response = self.client.post(
                    reverse('login'),
                    {'uid': uid, 'password': pwd},
                    **headers
                )
                
                # Assert based on expected outcome
                if uid == 'valid_user' and pwd == 'valid_pass':
                    self.assertRedirects(response, reverse('index'))
                else:
                    self.assertContains(response, 'Invalid UID or password')  # Adjusted error message