import os
import subprocess
from pathlib import PurePosixPath
from django.conf import settings
import cloudinary
import cloudinary.uploader

# WICHTIG: Cloudinary im Worker-Prozess konfigurieren
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_folder_to_cloudinary(local_folder: str, cloudinary_folder: str) -> None:
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            file_path = os.path.join(root, file)
            # relative Pfade immer in POSIX (/), keine Backslashes
            relative_path = os.path.relpath(file_path, local_folder).replace("\\", "/")
            public_id = str(PurePosixPath(cloudinary_folder) / relative_path)

            cloudinary.uploader.upload(
                file_path,
                public_id=public_id,
                resource_type="raw",   # HLS: .m3u8 und .ts als RAW ausliefern
                overwrite=True
            )

def convert_video(source: str, video_id: int, resolution: int, suffix: str) -> None:
    """
    Convert video to HLS format with m3u8 playlist and upload all outputs to Cloudinary.
    """
    output_dir = os.path.join(settings.MEDIA_ROOT, "videos", str(video_id), suffix)
    os.makedirs(output_dir, exist_ok=True)

    target = os.path.join(output_dir, "index.m3u8")

    cmd = [
        "ffmpeg",
        "-i", source,
        "-vf", f"scale=-2:{resolution}",
        "-c:v", "h264",
        "-profile:v", "main",
        "-crf", "20",
        "-g", "48",
        "-keyint_min", "48",
        "-sc_threshold", "0",
        "-hls_time", "4",
        "-hls_playlist_type", "vod",
        "-b:v", "1000k",
        "-maxrate", "1200k",
        "-bufsize", "2000k",
        "-c:a", "aac",
        "-b:a", "128k",
        "-hls_segment_filename", os.path.join(output_dir, "index%d.ts"),
        target,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        # Logge FFmpeg-Fehler, damit du sie in Heroku logs siehst
        print("FFmpeg error:", result.stderr)
        return

    # Alle generierten Dateien zu Cloudinary hochladen (als RAW)
    cloudinary_folder = f"videos/{video_id}/{suffix}"
    upload_folder_to_cloudinary(output_dir, cloudinary_folder)

    
    