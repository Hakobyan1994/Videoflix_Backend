import subprocess
import os
from django.conf import settings
import cloudinary.uploader


def upload_folder_to_cloudinary(local_folder, cloudinary_folder):
    for root, dirs, files in os.walk(local_folder):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, local_folder)
            public_id = f"{cloudinary_folder}/{relative_path}"

            cloudinary.uploader.upload(
                file_path,
                public_id=public_id,
                resource_type="auto",
                overwrite=True
            )

def convert_video(source, video_id, resolution, suffix):
    """Convert video to HLS format with m3u8 playlist"""
    output_dir = os.path.join(
        settings.MEDIA_ROOT,
        'videos',
        str(video_id),
        suffix
    )
    os.makedirs(output_dir, exist_ok=True)

    target = os.path.join(output_dir, 'index.m3u8')

    cmd = [
        'ffmpeg',
        '-i', source,
        '-vf', f'scale=-2:{resolution}',
        '-c:v', 'h264',
        '-profile:v', 'main',
        '-crf', '20',
        '-g', '48',
        '-keyint_min', '48',
        '-sc_threshold', '0',
        '-hls_time', '4',
        '-hls_playlist_type', 'vod',
        '-b:v', '1000k',
        '-maxrate', '1200k',
        '-bufsize', '2000k',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-hls_segment_filename', os.path.join(output_dir, 'index%d.ts'),
        target
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("FFmpeg error:", result.stderr)
        return

    # Hochladen aller generierten Dateien zu Cloudinary
    cloudinary_folder = f"videos/{video_id}/{suffix}"
    upload_folder_to_cloudinary(output_dir, cloudinary_folder)


    