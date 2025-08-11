from .models import Video
from django.dispatch import receiver
from django.db.models.signals import post_delete, post_save
from .tasks import convert_video
import os
import django_rq



@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created:
        q = django_rq.get_queue("default")
        q.enqueue(convert_video, instance.file.path, instance.id, 480,  "480p")
        q.enqueue(convert_video, instance.file.path, instance.id, 720,  "720p")
        q.enqueue(convert_video, instance.file.path, instance.id, 1080, "1080p")


@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem when corresponding Video object is deleted.
    """
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)

    base, ext = os.path.splitext(instance.file.path)
    converted_files = [base + '_480p.mp4', base + '_720p.mp4', base + '_1080p.mp4']
    for file_path in converted_files:
        if os.path.isfile(file_path):
            os.remove(file_path)
  
    if instance.thumbnail_url:
        instance.thumbnail_url.delete(save=False)
