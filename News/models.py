from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from ckeditor.fields import RichTextField


class News(models.Model):
    """Новости"""

    title = models.CharField(
        max_length=255, verbose_name="заголовок новости", unique=True
    )

    text = RichTextField(verbose_name="Содержание новости")
    image = models.FileField(
        null=True,
        upload_to="news/%Y/%m/%d/",
        verbose_name="Файл",
        help_text="Изображение для новости",)
    breaking = models.BooleanField(verbose_name="Срочная новость", default=False)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Создан")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Новость"
        verbose_name_plural = "Новости"

    def image_tag(self):
        """тег для image"""
        if self.image:
            return format_html(
                "<img src='/static/media/{}'\
             width='400'/>".format(
                    self.image
                )
            )

    def __str__(self):
        return self.title


