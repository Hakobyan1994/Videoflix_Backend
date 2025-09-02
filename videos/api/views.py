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
import os,requests
from django.views.decorators.http import require_http_methods
from django.http import StreamingHttpResponse, HttpResponseNotFound


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
    


CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")

def _raw_url(public_id: str) -> str:
    # raw delivery (passt zu deinem Upload resource_type="raw")
    return f"https://res.cloudinary.com/{CLOUD_NAME}/raw/upload/{public_id}"

def _ctype(name: str) -> str:
    return "application/vnd.apple.mpegurl" if name.endswith(".m3u8") else "video/MP2T"

@require_http_methods(["GET"])
def serve_hls(request, video_id: int, suffix: str, filename: str):
    public_id = f"videos/{video_id}/{suffix}/{filename}"
    url = _raw_url(public_id)

    # Range durchreichen (wichtig für .ts)
    headers = {}
    rng = request.headers.get("Range")
    if rng: headers["Range"] = rng

    r = requests.get(url, headers=headers, stream=True, timeout=60)
    if r.status_code == 404:
        return HttpResponseNotFound("HLS file not ready")

    status = r.status_code if r.status_code in (200, 206) else 200

    resp = StreamingHttpResponse(r.iter_content(64 * 1024), status=status, content_type=_ctype(filename))
    # sinnvolle Header weiterreichen
    if r.headers.get("Content-Range"): resp["Content-Range"] = r.headers["Content-Range"]
    if r.headers.get("Accept-Ranges"): resp["Accept-Ranges"] = r.headers["Accept-Ranges"]
    if r.headers.get("Content-Length"): resp["Content-Length"] = r.headers["Content-Length"]
    # optional Caching
    resp["Cache-Control"] = "public, max-age=300"
    return resp


