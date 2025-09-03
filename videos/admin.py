from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from .models import Video
import os

class VideoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "title", "category", "uploaded_at", "updated_at",
        "thumbnail_preview", "has_file",
    )
    list_filter = ("category", "uploaded_at")
    search_fields = ("title", "description", "category")
    ordering = ("-uploaded_at",)
    date_hierarchy = "uploaded_at"
    list_per_page = 50
    readonly_fields = ("uploaded_at", "updated_at", "thumbnail_preview")

    fieldsets = (
        ("Basis", {
            "fields": ("title", "description", "category")
        }),
        ("Dateien", {
            "fields": ("file", "thumbnail_preview"),
        }),
        ("Meta", {
            "fields": ("uploaded_at", "updated_at"),
        }),
    )

    def thumbnail_preview(self, obj):
        if not obj.pk:
            return "—"
        rel = f"thumbnails/{obj.id}.jpg"
        abs_path = os.path.join(settings.MEDIA_ROOT, rel)
        if os.path.isfile(abs_path):
            return format_html(
                '<img src="{}{}" style="height:60px;border-radius:6px;object-fit:cover;" />',
                settings.MEDIA_URL, rel
            )
        return "—"
    thumbnail_preview.short_description = "Thumbnail"

    def has_file(self, obj):
        return bool(obj.file)
    has_file.boolean = True
    has_file.short_description = "Original vorhanden"

admin.site.register(Video, VideoAdmin)     
  