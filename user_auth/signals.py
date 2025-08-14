from django.dispatch import receiver
from .models import User
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model


User=get_user_model()

@receiver(post_save, sender=User)
def auto_activate_admin(sender,instance,created, **kwargs):
    if created and (instance.is_staff or instance.is_superuser):
        User.objects.filter(pk=instance.pk).update(is_active=True)