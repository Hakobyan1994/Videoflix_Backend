from videos.models import Video
from.serializers import VideoSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework import status, permissions
from pathlib import Path
from django.http import FileResponse, Http404
from django.conf import settings
from django.shortcuts import redirect
import cloudinary
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)





class VideoList(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self,request,):
        category = request.query_params.get('category') 
        videos = Video.objects.all()
        if category:
            category = category.strip()            
            videos = videos.filter(category__iexact=category)
        serializer = VideoSerializer(videos, many=True,context={'request': request})
        return Response(serializer.data,status=status.HTTP_200_OK) 
        

    
class VideoDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self, pk):
        try:
            return Video.objects.get(pk=pk)
        except Video.DoesNotExist:
            raise Http404

    def get(self,request,pk):
        video = self.get_object(pk)
        serializer = VideoSerializer(video,context={'request': request})
        return Response(serializer.data,status=status.HTTP_200_OK)

def serve_hls(request, video_id: int, suffix: str, filename: str):
    # Statt lokaler Datei → 302 Redirect zur Cloudinary-URL
    url, _ = cloudinary.utils.cloudinary_url(
        f"videos/{video_id}/{suffix}/{filename}",
        resource_type="raw",  # .m3u8 und .ts als "raw" ausliefern
        secure=True,
    )
    return redirect(url)


