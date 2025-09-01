from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.staticfiles import finders 
from django.core.mail import EmailMultiAlternatives 
from email.mime.image import MIMEImage
import os


def get_display_username(user):
    username = getattr(user, "first_name", "").strip()

    if not username:
        email_or_username = getattr(user, "username", "User")
        local_part = email_or_username.split("@")[0]
        for sep in [".", "_", "-", "+"]:
            if sep in local_part:
                local_part = local_part.split(sep)[0]
                break
        username = local_part
    return username.capitalize()
   

def send_activation_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_link = f"https://vidoflix-app.com/pages/auth/activate.html?uid={uid}&token={token}"
    context = {
        "username": get_display_username(user),
        "project_name": "Videoflix",
        "reset_link": reset_link,
    }

    html_content = render_to_string("emails/activation_email.html", context)


    email = EmailMultiAlternatives(
        subject="Confirm your email",
        body="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_content, "text/html")

    logo_path = os.path.join(
        settings.BASE_DIR, "user_auth", "templates", "emails", "videoflix.png"
    )

    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            img = MIMEImage(f.read())
        img.add_header("Content-ID", "<logo>")
        img.add_header("Content-Disposition", "inline", filename="videoflix.png")
        email.mixed_subtype = "related"
        email.attach(img)

    email.send()




def send_password_reset_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    frontend_base_url = 'https://vidoflix-app.com/pages/auth/confirm_password.html'
    reset_link = f"{frontend_base_url}?uid={uid}&token={token}"
    context = {
        "username": get_display_username(user),
        "project_name": "Videoflix",
        "reset_link": reset_link,
    }
    html_content = render_to_string("emails/reset_password.html", context)
    email = EmailMultiAlternatives(
        subject="Reset your password",
        body="",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_content, "text/html")

    logo_path = os.path.join(
        settings.BASE_DIR, "user_auth", "templates", "emails", "videoflix.png"
    )

    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            img = MIMEImage(f.read())
        img.add_header("Content-ID", "<logo>")
        img.add_header("Content-Disposition", "inline", filename="videoflix.png")
        email.mixed_subtype = "related"
        email.attach(img)

    email.send()