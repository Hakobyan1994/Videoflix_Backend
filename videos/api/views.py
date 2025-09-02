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
import os
import boto3
from botocore.exceptions import ClientError
from django.http import StreamingHttpResponse, HttpResponseNotFound, HttpResponse
from django.views.decorators.http import require_http_methods





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

AWS_BUCKET = os.getenv("BUCKETEER_BUCKET_NAME")
AWS_REGION = os.getenv("BUCKETEER_AWS_REGION")

# Boto3-Client mit deinen ENV-Credentials (Bucketeer setzt sie in Heroku)
s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("BUCKETEER_AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("BUCKETEER_AWS_SECRET_ACCESS_KEY"),
)

def _ctype(name: str) -> str:
    return "application/vnd.apple.mpegurl" if name.endswith(".m3u8") else "video/MP2T"

@require_http_methods(["GET"])
def serve_hls(request, video_id: int, suffix: str, filename: str):
    """
    Streamt index.m3u8 und .ts direkt aus S3 (privater Bucket) → same-origin für den Browser.
    Unterstützt Range (wichtig für .ts).
    """
    key = f"videos/{video_id}/{suffix}/{filename}"

    # Range-Header übernehmen (für .ts Segmente)
    get_kwargs = {"Bucket": AWS_BUCKET, "Key": key}
    range_header = request.headers.get("Range") or request.META.get("HTTP_RANGE")
    if range_header:
        get_kwargs["Range"] = range_header  # z.B. "bytes=0-"

    try:
        obj = s3.get_object(**get_kwargs)
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code in ("NoSuchKey", "404"):
            return HttpResponseNotFound("File not found")
        # Falls Range außerhalb → 416 etc.
        status = int(e.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 404))
        return HttpResponse(status=status)

    body = obj["Body"]  # StreamingBody
    status = 206 if "ContentRange" in obj else 200

    resp = StreamingHttpResponse(
        streaming_content=body.iter_chunks(chunk_size=64 * 1024),
        status=status,
        content_type=_ctype(filename),
    )
    # sinnvolle Header
    if "ContentLength" in obj:
        resp["Content-Length"] = str(obj["ContentLength"])
    resp["Accept-Ranges"] = "bytes"
    if "ContentRange" in obj:
        resp["Content-Range"] = obj["ContentRange"]
    resp["Cache-Control"] = "public, max-age=300"
    return resp


