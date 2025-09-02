from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from django.core.files.storage import default_storage
from django.conf import settings
from .models import Video

import os
import django_rq

# WICHTIG: beide Funktionen aus tasks importieren
from .tasks import convert_video, generate_thumbnail


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        q = django_rq.get_queue("default")
        src = instance.file.name  # Storage-Key, NICHT .path
        q.enqueue(convert_video, src, instance.id, 480,  "480p")
        q.enqueue(convert_video, src, instance.id, 720,  "720p")
        q.enqueue(convert_video, src, instance.id, 1080, "1080p")
        q.enqueue(generate_thumbnail, src, instance.id)


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    # Lokale Dateien löschen ist auf Heroku eigentlich überflüssig,
    # aber falls im Storage noch was liegt, könntest du optional auch
    # S3-Keys entfernen. Minimal lassen wir es so:
    try:
        if instance.file and os.path.isfile(getattr(instance.file, "path", "")):
            os.remove(instance.file.path)
    except Exception:
        pass