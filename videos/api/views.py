from videos.models import Video
from.serializers import VideoSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework import status
from pathlib import Path
from django.http import FileResponse, Http404
from django.conf import settings


class VideoList(APIView):
    def get(self,request,):
        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True,context={'request': request})
        return Response(serializer.data,status=status.HTTP_200_OK) 
    
class VideoDetail(APIView):
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
    """
    Liefert sowohl index.m3u8 als auch jedes segment_xxx.ts
    → /api/video/<id>/<suffix>/<filename>
    """
    file_path = (
        Path(settings.MEDIA_ROOT) /
        "videos" / str(video_id) / suffix / filename
    )
    if file_path.exists():
        ctype = (
            "application/vnd.apple.mpegurl"
            if filename.endswith(".m3u8")
            else "video/MP2T"
        )
        return FileResponse(file_path.open("rb"), content_type=ctype)
    raise Http404


