# tests/test_services.py

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from accounts.models import User, UserTypes
from courses.models import Course
from crm.services.clients import ClientService, PasswordService
from assignments.models import Assignment


class ClientServiceTestCase(TestCase):
    def setUp(self):
        # Create a teacher & course so assignments can FK to a real course
        self.teacher = User.objects.create_user(
            username="teach", email="t@example.com", password="pass", user_type=UserTypes.teacher
        )
        # Assign teacher directly (no profile)
        self.course = Course.objects.create(
            title="Dummy Course",
            teacher=self.teacher
        )
        # A bare user for registration tests
        self.user = User.objects.create(
            username="jdoe",
            email="jdoe@example.com",
            password=""
        )
        self.client_svc = ClientService(request=None)

    def test_register_sets_all_fields_and_marks_complete(self):
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+1234567890",
            "gender": "M",
        }
        user, error = self.client_svc.register(payload, self.user)
        self.assertIsNone(error)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
        self.assertEqual(self.user.phone_number, "+1234567890")
        self.assertEqual(self.user.gender, "M")
        self.assertTrue(self.user.registration_complete)

    def test_filter_qs_by_date_filters_correctly(self):
        now = timezone.now()
        # create three assignments, then override their created_at
        common = {
            "course": self.course,
            "description": "",
            "due_date": now.date() + timedelta(days=1),
        }
        a1 = Assignment.objects.create(title="A1", **common)
        a2 = Assignment.objects.create(title="A2", **common)
        a3 = Assignment.objects.create(title="A3", **common)

        # override created_at via update to bypass auto_now_add
        Assignment.objects.filter(pk=a1.pk).update(created_at=now - timedelta(days=10))
        Assignment.objects.filter(pk=a2.pk).update(created_at=now - timedelta(days=5))
        Assignment.objects.filter(pk=a3.pk).update(created_at=now + timedelta(days=1))

        qs = Assignment.objects.all()

        # start_date only: should include A2 and A3
        filtered = self.client_svc.filter_qs_by_date(
            qs,
            start_date=(now - timedelta(days=7)).date()
        )
        titles = [a.title for a in filtered]
        self.assertNotIn("A1", titles)
        self.assertIn("A2", titles)
        self.assertIn("A3", titles)

        # start + end: only A2
        filtered2 = self.client_svc.filter_qs_by_date(
            qs,
            start_date=(now - timedelta(days=7)).date(),
            end_date=now.date()
        )
        titles2 = [a.title for a in filtered2]
        self.assertNotIn("A1", titles2)
        self.assertIn("A2", titles2)
        self.assertNotIn("A3", titles2)


class PasswordServiceTestCase(TestCase):
    def setUp(self):
        self.raw_password = "OldPass@123"
        self.user = User.objects.create_user(
            username="psmith",
            email="psmith@example.com",
            password=self.raw_password,
        )
        self.pwd_svc = PasswordService(request=None)

    def test_verify_password_true(self):
        self.assertTrue(
            self.pwd_svc.verify_password(self.raw_password, self.user.password)
        )

    def test_verify_password_false(self):
        self.assertFalse(
            self.pwd_svc.verify_password("wrongpass", self.user.password)
        )

    def test_update_password_rejects_wrong_old_password(self):
        payload = {"old_password": "wrongpass", "new_password": "NewPass@456"}
        result, error = self.pwd_svc.update_password(payload, self.user)
        self.assertIsNone(result)
        self.assertEqual(error, "Password Incorrect")

    def test_update_password_succeeds_and_hashes(self):
        new_pw = "NewPass@456"
        payload = {"old_password": self.raw_password, "new_password": new_pw}
        msg, error = self.pwd_svc.update_password(payload, self.user)
        self.assertIsNone(error)
        self.assertEqual(msg, "Password set successfully")

        self.user.refresh_from_db()
        self.assertTrue(self.pwd_svc.verify_password(new_pw, self.user.password))
        self.assertFalse(self.pwd_svc.verify_password(self.raw_password, self.user.password))
