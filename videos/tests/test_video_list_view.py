# videos/tests/test_video_list_view.py
import os
import shutil
import tempfile
from django.urls import reverse
from django.test import override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from videos.models import Video


class VideoListTests(APITestCase):
    def setUp(self):
        self.tmp_media = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.tmp_media, MEDIA_URL="/media/")
        self.override.enable()

        self.url = reverse("video-list")

        self.vid_bytes = b"\x00" * 1024 
        self.img_bytes = b"\x89PNG\r\n"  

       
        Video.objects.create(
            title="Video A",
            description="Desc A",
            category="Drama",
            file=SimpleUploadedFile("video_a.mp4", self.vid_bytes, content_type="video/mp4"),
            thumbnail_url=SimpleUploadedFile("thumb_a.jpg", self.img_bytes, content_type="image/jpeg"),
        )
        Video.objects.create(
            title="Video B",
            description="Desc B",
            category="Action",
            file=SimpleUploadedFile("video_b.mp4", self.vid_bytes, content_type="video/mp4"),
            thumbnail_url=SimpleUploadedFile("thumb_b.jpg", self.img_bytes, content_type="image/jpeg"),
        )

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.tmp_media, ignore_errors=True)

    def test_video_list_success(self):
        resp = self.client.get(self.url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
        self.assertEqual(len(resp.data), 2)
        item = resp.data[0]
        for key in ("id", "uploaded_at", "updated_at", "title", "description", "file", "thumbnail_url", "category"):
            self.assertIn(key, item)
        self.assertTrue(item["file"].startswith("http://testserver/media/"))
        self.assertTrue(item["thumbnail_url"].startswith("http://testserver/media/"))

    def test_video_list_empty(self):
        Video.objects.all().delete()
        resp = self.client.get(self.url, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])
