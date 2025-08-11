from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase



User = get_user_model()
class LoginTests(APITestCase):

    def setUp(self):
       self.login_url=reverse("token_obtain_pair")
       self.refresh_url=reverse("token_refresh") 

       self.email="test@example.com"
       self.password="testtest123456"
       self.user = User.objects.create_user(
            username=self.email,
            email=self.email,
            password=self.password,
            is_active=True,
        )
       
       self.valid_login={"email": self.email, "password": self.password}



    def test_login_success_sets_cookies(self):
        response = self.client.post(self.login_url, self.valid_login, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Login erfolgreich")
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token",response.cookies)

    def test_login_email_not_found(self):
        payload={**self.valid_login,"email":"wrong@example.com"}
        response=self.client.post(self.login_url,payload,format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertIn("Benutzer mit dieser E-Mail existiert nicht.", response.data["non_field_errors"])
        self.assertNotIn("access_token", response.cookies)
        self.assertNotIn("refresh_token", response.cookies)

    def test_login_password_not_found(self):
        payload={**self.valid_login,"password":"wrongpassword"} 
        response=self.client.post(self.login_url,payload,format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors",response.data)
        self.assertIn("Falsches Passwort.", response.data["non_field_errors"])
        self.assertNotIn("access_token", response.cookies)
        self.assertNotIn("refresh_token", response.cookies)


    def test_login_missing_required_fields(self):
        response = self.client.post(self.login_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in ("email", "password"):
            self.assertIn(field, response.data)
            self.assertEqual(str(response.data[field][0]), "This field is required.")
            self.assertEqual(response.data[field][0].code, "required")    


    def test_refresh_success_with_cookie(self):
        login_resp = self.client.post(self.login_url, self.valid_login, format="json")
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        refresh_resp = self.client.post(self.refresh_url, {}, format="json")
        self.assertEqual(refresh_resp.status_code, status.HTTP_200_OK)
        self.assertIn("access_token", refresh_resp.cookies)

    def test_refresh_without_cookie_returns_400(self):
        self.client.cookies.clear()
        response = self.client.post(self.refresh_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Kein Refresh-Token gefunden.")    
