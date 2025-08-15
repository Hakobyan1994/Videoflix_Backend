
from videos.models import Video
from rest_framework import serializers,status
from rest_framework.views import APIView
from rest_framework.response import Response
import os
from urllib.parse import urljoin
from django.conf import settings


class VideoSerializer(serializers.ModelSerializer):
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ["id", "uploaded_at", "updated_at", "title", "description", "file", "category", "thumbnail_url"]
        read_only_fields = ("id", "uploaded_at", "updated_at", "thumbnail_url")

    def get_thumbnail_url(self, obj):
        rel = f"thumbnails/{obj.id}.jpg"
        abs_path = os.path.join(settings.MEDIA_ROOT, rel)
        if os.path.isfile(abs_path):
            request = self.context.get("request")
            return request.build_absolute_uri(urljoin(settings.MEDIA_URL, rel))
        return None
