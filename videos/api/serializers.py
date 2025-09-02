
from videos.models import Video
from rest_framework import serializers,status
from rest_framework.views import APIView
from rest_framework.response import Response
import os
from urllib.parse import urljoin
from django.conf import settings
from django.core.files.storage import default_storage

class VideoSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ["id", "uploaded_at", "updated_at", "title", "description", "file", "category", "thumbnail_url"]
        read_only_fields = ("id", "uploaded_at", "updated_at", "thumbnail_url")

    def get_thumbnail_url(self, obj):
        key = f"thumbnails/{obj.id}.jpg"
        try:
            return self.context["request"].build_absolute_uri(default_storage.url(key))
        except Exception:
            return None