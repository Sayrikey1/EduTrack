# tests/test_auth_flow.py
import random
import string
from django.urls import reverse
from django.test import override_settings
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch

from accounts.models import User, UserTypes, RegisterLog


def generate_test_user():
    first_names = ["Test_User", "Demo_User", "Auth_User"]
    domains = ["gmail.com", "yahoo.com", "zest.com"]
    username = f"{random.choice(first_names)}_{''.join(random.choices(string.digits, k=4))}"
    return {
        "username": username,
        "email": f"{username}@{random.choice(domains)}",
        "password": "SecurePass123!",
        "phone_number": "+2348012345678",
        "dob": "2000-01-01",
        "gender": "male"
    }

@override_settings(DEBUG=True)
class AuthFlowTests(APITestCase):
    def setUp(self):
        # Ensure DEBUG and patch Celery
        patcher_email = patch('accounts.tasks.send_activation_otp_email_queue.delay', lambda *args, **kwargs: None)
        self.addCleanup(patcher_email.stop)
        patcher_email.start()

        # Register a student once
        self.client = APIClient()
        self.user_data = generate_test_user()
        signup_resp = self.client.post(
            reverse("signup"),
            {
                "email": self.user_data["email"],
                "full_name": f"Test {self.user_data['username']}",
                "password": self.user_data["password"]
            }
        )
        self.assertEqual(signup_resp.status_code, status.HTTP_200_OK)
        self.student_email = signup_resp.data["data"]["email"]

        # OTP should be "123456" in DEBUG
        otp_record = RegisterLog.objects.get(email=self.student_email)
        self.assertTrue(otp_record.otp)

        # Verify OTP
        verify_resp = self.client.post(
            reverse("verify-otp"), {"email": self.student_email, "otp": "123456"}
        )
        self.assertEqual(verify_resp.status_code, status.HTTP_200_OK)

        # Complete registration
        reg_resp = self.client.post(
            reverse("student_registration"),
            {
                "email": self.student_email,
                "username": self.user_data["username"],
                "phone_number": self.user_data["phone_number"],
                "dob": self.user_data["dob"],
                "gender": self.user_data["gender"]
            }
        )
        self.assertEqual(reg_resp.status_code, status.HTTP_200_OK)

    def test_full_student_flow(self):
        user = User.objects.get(email=self.student_email)
        self.assertEqual(user.user_type, UserTypes.student)

    def test_login_flow(self):
        login_resp = self.client.post(
            reverse("login"),
            {"username": self.student_email, "password": self.user_data["password"]}
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", login_resp.data)
        self.assertIn("refresh_token", login_resp.data)
