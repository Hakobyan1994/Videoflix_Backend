import subprocess
import os
from django.conf import settings
from django.core.files.storage import default_storage

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
    
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            local_path = os.path.join(root, file)
            s3_path = f"videos/{video_id}/{suffix}/{file}"
            with open(local_path, 'rb') as f:
                default_storage.save(s3_path, f)


    