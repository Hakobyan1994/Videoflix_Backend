from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

class LogoutViewTests(APITestCase):
    def setUp(self):
        self.url = reverse("logout")  


    def test_logout_with_cookies(self):
        self.client.cookies["access_token"] = "dummy-access"
        self.client.cookies["refresh_token"] = "dummy-refresh"
        resp = self.client.post(self.url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get("message"), "Erfolgreich ausgeloggt.")
        self.assertIn("access_token", resp.cookies)
        self.assertIn("refresh_token", resp.cookies)
        self.assertEqual(resp.cookies["access_token"].value, "")
        self.assertEqual(resp.cookies["refresh_token"].value, "")
        self.assertEqual(int(resp.cookies["access_token"]["max-age"]), 0)
        self.assertEqual(int(resp.cookies["refresh_token"]["max-age"]), 0)