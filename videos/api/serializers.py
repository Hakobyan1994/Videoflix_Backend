
from videos.models import Video
from rest_framework import serializers,status
from rest_framework.views import APIView
from rest_framework.response import Response
from collections import defaultdict

class VideoSerializer(serializers.ModelSerializer):

      class Meta:
            model = Video
            fields = '__all__'
