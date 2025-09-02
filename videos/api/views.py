from videos.models import Video
from.serializers import VideoSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework import status, permissions
from pathlib import Path
from django.http import FileResponse, Http404
from django.conf import settings
import requests
from django.http import StreamingHttpResponse, HttpResponseNotFound
from django.views.decorators.http import require_http_methods
from django.conf import settings


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

@require_http_methods(["GET"])
def serve_hls(request, video_id: int, suffix: str, filename: str):
    url = f"{settings.MEDIA_URL}videos/{video_id}/{suffix}/{filename}"

    r = requests.get(url, stream=True)
    if r.status_code == 404:
        return HttpResponseNotFound("File not found")

    content_type = "application/vnd.apple.mpegurl" if filename.endswith(".m3u8") else "video/MP2T"
    response = StreamingHttpResponse(r.iter_content(chunk_size=8192), content_type=content_type)
    response['Cache-Control'] = 'public, max-age=300'
    return response


