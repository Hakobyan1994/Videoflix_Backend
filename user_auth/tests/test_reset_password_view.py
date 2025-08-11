from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="noreply@test.local")

class PasswordResetTests(APITestCase):
    def setUp(self):
        self.url = reverse("password_reset")
        email = "user@example.com"
        self.user = User.objects.create_user(
            username=email,
            email=email,
            password="irrelevant",
            is_active=True
        )
        self.valid = {"email": self.user.email}

    def test_reset_password_success_sends_email(self):
     resp = self.client.post(self.url, self.valid, format="json")
     self.assertEqual(resp.status_code, status.HTTP_200_OK)
     self.assertEqual(resp.data["message"], "Password reset email sent")
     self.assertEqual(len(mail.outbox), 1)
     sent_email = mail.outbox[0]
     self.assertEqual(sent_email.from_email, "noreply@test.local")
     self.assertIn(self.user.email, sent_email.to)
     self.assertIn("Passwort zurücksetzen", sent_email.subject)
     self.assertIn("http://127.0.0.1:5500/pages/auth/confirm_password.html", sent_email.body)
     self.assertIn("uid=", sent_email.body)
     self.assertIn("token=", sent_email.body)

    def test_missing_email_field(self):
        resp = self.client.post(self.url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", resp.data)
        self.assertEqual(str(resp.data["email"][0]), "This field is required.")
        self.assertEqual(len(mail.outbox), 0)

    def test_wrong_email(self):
        payload = {**self.valid, "email": "wrongemail@web.com"}
        resp = self.client.post(self.url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", resp.data)
        self.assertIn("No user found with this email.", resp.data["email"])
        self.assertEqual(len(mail.outbox), 0)


