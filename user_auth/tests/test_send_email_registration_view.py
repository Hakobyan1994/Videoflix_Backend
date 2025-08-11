from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="noreply@test.local",
)
class RegistrationEmailTests(APITestCase):
    def setUp(self):
        self.url = reverse("register")
        self.valid_payload = {
            "email": "user@example.com",
            "password": "secret123",
            "confirmed_password": "secret123",
        }

    def test_register_sends_activation_email(self):
        resp = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]

        self.assertEqual(msg.subject, "Bitte aktiviere dein Konto")
        self.assertEqual(msg.from_email, "noreply@test.local")
        self.assertEqual(msg.to, ["user@example.com"])

        # Body sollte Link mit uid & token enthalten
        self.assertIn("activate.html?uid=", msg.body)
        self.assertIn("&token=", msg.body)

        # uid/token fachlich korrekt?
        user = User.objects.get(email="user@example.com")
        expected_uid = urlsafe_base64_encode(force_bytes(user.pk))
        expected_token = default_token_generator.make_token(user)

        self.assertIn(expected_uid, msg.body)
        self.assertIn(expected_token, msg.body)

    def test_no_email_sent_on_invalid_payload(self):
        bad = {"email": "user@example.com", "password": "short", "confirmed_password": "short"}
        resp = self.client.post(self.url, bad, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)
