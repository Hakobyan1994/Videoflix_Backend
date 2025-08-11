from django.db import models

# Create your models here.
from django.db import models

class Video(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=1000, blank=True)
    file = models.FileField(upload_to='videos/')
    thumbnail_url = models.FileField(upload_to='thumbnails/')
    category = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.title
