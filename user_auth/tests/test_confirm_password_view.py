from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

class PasswordResetConfirmTests(APITestCase):
    def setUp(self):
        email = "user@example.com"
        self.user = User.objects.create_user(
            username=email,
            email=email,
            password="oldpassword123",
            is_active=True,
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = lambda uid, tok: reverse(
            "password_reset_confirm",
            kwargs={"uidb64": uid, "token": tok},
        )

    def test_confirm_success(self):
        payload = {
            "new_password": "NewSecret123",
            "confirm_password": "NewSecret123",
        }
        resp = self.client.post(self.url(self.uidb64, self.token), payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["message"], "Password reset successful")
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewSecret123"))

    def test_missing_fields(self):
        resp = self.client.post(self.url(self.uidb64, self.token), {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", resp.data)
        self.assertEqual(str(resp.data["new_password"][0]), "This field is required.")
        self.assertIn("confirm_password", resp.data)
        self.assertEqual(str(resp.data["confirm_password"][0]), "This field is required.")

    def test_password_too_short(self):
        payload = {"new_password": "short", "confirm_password": "short"}
        resp = self.client.post(self.url(self.uidb64, self.token), payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password", resp.data)


    def test_password_mismatch(self):
        payload = {"new_password": "NewSecret123", "confirm_password": "Different123"}
        resp = self.client.post(self.url(self.uidb64, self.token), payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", resp.data)
        self.assertIn("Passwords do not match.", resp.data["non_field_errors"])

    def test_invalid_uid(self):
        bad_uid = "AAA"  
        resp = self.client.post(self.url(bad_uid, self.token), {
            "new_password": "NewSecret123",
            "confirm_password": "NewSecret123",
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["error"], "Invalid link")

    def test_invalid_token(self):
        bad_token = "invalid-token"
        resp = self.client.post(self.url(self.uidb64, bad_token), {
            "new_password": "NewSecret123",
            "confirm_password": "NewSecret123",
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["error"], "Invalid or expired token")




         

