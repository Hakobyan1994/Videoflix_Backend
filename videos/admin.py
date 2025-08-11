from django.contrib import admin
from .models import Video
# Register your models here.
from django.utils.html import format_html

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
            "fields": ("file", "thumbnail_url", "thumbnail_preview"),
        }),
        ("Meta", {
            "fields": ("uploaded_at", "updated_at"),
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.thumbnail_url:
            try:
                return format_html(
                    '<img src="{}" style="height:60px;border-radius:6px;object-fit:cover;" />',
                    obj.thumbnail_url.url
                )
            except Exception:
                return "—"
        return "—"
    thumbnail_preview.short_description = "Thumbnail"

    def has_file(self, obj):
        return bool(obj.file)
    has_file.boolean = True
    has_file.short_description = "Original vorhanden"

admin.site.register(Video,VideoAdmin)        
  