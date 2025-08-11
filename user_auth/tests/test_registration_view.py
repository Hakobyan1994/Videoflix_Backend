from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

User = get_user_model()
class RegistrationTests(APITestCase):
    def setUp(self):
        self.url = reverse('register')
        self.valid = {
            "email": "user@example.com",
            "password": "secret123",
            "confirmed_password": "secret123",
        }


    @patch("user_auth.api.views.send_activation_email")
    def test_register_success(self, _mock_send):
        resp = self.client.post(self.url, self.valid, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("user_id", resp.data)
        self.assertEqual(resp.data["email"], self.valid["email"])
        self.assertEqual(User.objects.count(), 1)
        u = User.objects.get()
        self.assertEqual(u.email, self.valid["email"])
        self.assertEqual(u.username, self.valid["email"])  
        self.assertFalse(u.is_active) 

    @patch("user_auth.api.views.send_activation_email")
    def test_missing_all_required_fields(self, _mock_send):
        resp = self.client.post(self.url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("email", "password", "confirmed_password"):
            self.assertIn(field, resp.data)
            self.assertEqual(str(resp.data[field][0]), "This field is required.")
            self.assertEqual(resp.data[field][0].code, "required")
        self.assertEqual(User.objects.count(), 0)

    @patch("user_auth.api.views.send_activation_email")
    def test_missing_single_field_email(self, _mock_send):
        payload=self.valid.copy()
        payload.pop("email", None)
        resp = self.client.post(self.url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", resp.data)
        self.assertEqual(str(resp.data["email"][0]), "This field is required.")
        self.assertEqual(resp.data["email"][0].code, "required")
        self.assertEqual(User.objects.count(), 0)

    @patch("user_auth.api.views.send_activation_email")
    def test_missing_single_field_password(self, _mock_send):
        payload=self.valid.copy()
        payload.pop("password",None)
        resp = self.client.post(self.url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", resp.data)
        self.assertEqual(str(resp.data["password"][0]), "This field is required.")
        self.assertEqual(resp.data["password"][0].code, "required")
        self.assertEqual(User.objects.count(), 0)

    @patch("user_auth.api.views.send_activation_email")
    def test_missing_single_field_confirmed_password(self, _mock_send):
        payload=self.valid.copy()
        payload.pop("confirmed_password",None)
        resp = self.client.post(self.url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("confirmed_password", resp.data)
        self.assertEqual(str(resp.data["confirmed_password"][0]), "This field is required.")
        self.assertEqual(resp.data["confirmed_password"][0].code, "required")
        self.assertEqual(User.objects.count(), 0)

    @patch("user_auth.api.views.send_activation_email")
    def test_password_too_short(self, _mock_send):
        payload = {**self.valid, "password": "12345", "confirmed_password": "12345"}
        resp = self.client.post(self.url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", resp.data)
        self.assertIn("Password must be at least 6 characters long.", resp.data["password"])
        self.assertEqual(User.objects.count(), 0)

    @patch("user_auth.api.views.send_activation_email")
    def test_password_mismatch(self, _mock_send):
        payload = {**self.valid, "confirmed_password": "different123"}
        resp = self.client.post(self.url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", resp.data)
        self.assertIn("Passwords dont match.", resp.data["password"])
        self.assertEqual(User.objects.count(), 0)

    @patch("user_auth.api.views.send_activation_email")
    def test_duplicate_email(self, _mock_send):
        User.objects.create_user(
            username=self.valid["email"],
            email=self.valid["email"],
            password="irrelevant",
            is_active=False,
        )
        resp = self.client.post(self.url, self.valid, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", resp.data)
        self.assertIn("Email is already in use.", resp.data["email"])
        self.assertEqual(User.objects.count(), 1)