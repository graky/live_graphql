from News.models import News
from django.contrib import admin


class NewsAdmin(admin.ModelAdmin):
    """Новости"""

    fieldsets = [
        (
            "Основные параметры",
            {"fields": ["created_at", "title", "breaking"]},
        ),
        ("Изображение", {"fields": [("image",)]}),
        ("Содержание", {"fields": ["text"]}),
    ]
    list_display = ["id", "title", "created_at", "breaking"]
    list_display_links = ["id", "title"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at"]
    list_per_page = 20


admin.site.register(News, NewsAdmin)
