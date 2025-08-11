from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def send_activation_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    frontend_base_url = 'http://127.0.0.1:5500/pages/auth/activate.html'
    reset_link = f"{frontend_base_url}?uid={uid}&token={token}"
    subject = "Bitte aktiviere dein Konto"
    message = f"Klicke auf den folgenden Link, um dein Konto zu aktivieren:\n\n{reset_link}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)

def send_password_reset_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    frontend_base_url = 'http://127.0.0.1:5500/pages/auth/confirm_password.html'
    reset_link = f"{frontend_base_url}?uid={uid}&token={token}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    subject = 'Passwort zurücksetzen'
    message = f'Klicke hier, um dein Passwort zurückzusetzen:\n\n{reset_link}'
    send_mail(subject, message, from_email, recipient_list)  