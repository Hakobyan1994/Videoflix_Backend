# core/storage_backends.py
from storages.backends.s3boto3 import S3Boto3Storage

class PublicMediaStorage(S3Boto3Storage):
    # Macht hochgeladene Dateien öffentlich lesbar (gut für <img src=...>)
    default_acl = "public-read"
    file_overwrite = False  # überschreibt gleichnamige Dateien nicht