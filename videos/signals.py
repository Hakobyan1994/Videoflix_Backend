from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from .tasks import convert_video
import os
import django_rq
from django.conf import settings
import subprocess

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        q = django_rq.get_queue("default")
        q.enqueue(convert_video, instance.file.path, instance.id, 480,  "480p")
        q.enqueue(convert_video, instance.file.path, instance.id, 720,  "720p")
        q.enqueue(convert_video, instance.file.path, instance.id, 1080, "1080p")
        q.enqueue(generate_thumbnail, instance.file.path, instance.id)


def generate_thumbnail(source, video_id):
    """Nimmt Frame bei 1 Sekunde und speichert als JPG."""
    thumbnails_dir = os.path.join(settings.MEDIA_ROOT, "thumbnails")
    os.makedirs(thumbnails_dir, exist_ok=True)
    output_path = os.path.join(thumbnails_dir, f"{video_id}.jpg")

    cmd = [
        "ffmpeg",
        "-ss", "00:00:01.000",  
        "-i", source,
        "-frames:v", "1",
        "-q:v", "2",
        "-y",
        output_path
    ]
    subprocess.run(cmd, capture_output=True, text=True)    



@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)

    base, ext = os.path.splitext(instance.file.path)
    converted_files = [base + '_480p.mp4', base + '_720p.mp4', base + '_1080p.mp4']
    for file_path in converted_files:
        if os.path.isfile(file_path):
            os.remove(file_path)

    thumb_path = os.path.join(settings.MEDIA_ROOT, "thumbnails", f"{instance.id}.jpg")
    if os.path.isfile(thumb_path):
        os.remove(thumb_path)