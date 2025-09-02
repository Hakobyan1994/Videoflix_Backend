# videos/tasks.py
import os, subprocess, tempfile, shutil
from django.core.files.storage import default_storage

def _download_to_tmp(storage_name: str) -> str:
    suffix = os.path.splitext(storage_name)[1] or ".mp4"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="/tmp")
    tmp_path = tmp.name
    with default_storage.open(storage_name, "rb") as src, open(tmp_path, "wb") as dst:
        shutil.copyfileobj(src, dst)
    return tmp_path

def convert_video(storage_name, video_id, resolution, suffix):
    # 1) Quelle aus Storage (S3) -> /tmp
    local_src = _download_to_tmp(storage_name)

    # 2) Ausgabeordner in /tmp
    out_dir = os.path.join("/tmp", "hls", str(video_id), suffix)
    os.makedirs(out_dir, exist_ok=True)
    m3u8_path = os.path.join(out_dir, "index.m3u8")
    ts_pattern = os.path.join(out_dir, "index%d.ts")

    # 3) FFmpeg
    cmd = [
        "ffmpeg","-y",
        "-i", local_src,
        "-vf", f"scale=-2:{resolution}",
        "-c:v","h264","-profile:v","main","-crf","20",
        "-g","48","-keyint_min","48","-sc_threshold","0",
        "-hls_time","4","-hls_playlist_type","vod",
        "-b:v","1000k","-maxrate","1200k","-bufsize","2000k",
        "-c:a","aac","-b:a","128k",
        "-hls_segment_filename", ts_pattern,
        m3u8_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("FFmpeg error:", result.stderr)
        try: os.unlink(local_src)
        except: pass
        return

    # 4) Ergebnisse in den Storage (S3)
    prefix = f"videos/{video_id}/{suffix}/"
    for root, _, files in os.walk(out_dir):
        for f in files:
            local_path = os.path.join(root, f)
            s3_key = prefix + f
            with open(local_path, "rb") as fh:
                default_storage.save(s3_key, fh)

    # 5) Aufräumen
    try: os.unlink(local_src)
    except: pass
    shutil.rmtree(os.path.join("/tmp", "hls", str(video_id)), ignore_errors=True)

def generate_thumbnail(storage_name, video_id):
    local_src = _download_to_tmp(storage_name)
    out_dir = "/tmp/thumbnails"; os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{video_id}.jpg")

    cmd = ["ffmpeg","-y","-ss","00:00:01.000","-i", local_src,"-frames:v","1","-q:v","2", out_path]
    subprocess.run(cmd, capture_output=True, text=True)

    s3_key = f"thumbnails/{video_id}.jpg"
    with open(out_path, "rb") as f: default_storage.save(s3_key, f)

    try: os.unlink(local_src)
    except: pass
    try: os.unlink(out_path)
    except: pass


    