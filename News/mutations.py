import graphene
from graphene_file_upload.scalars import Upload
from datetime import datetime
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import News, Comments
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core import serializers

CHANNEL_LAYER = get_channel_layer()


class AddNews(graphene.Mutation):
    """Добавляем новую новость"""

    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        title = graphene.String(required=True)
        text = graphene.String(required=True)
        breaking = graphene.Boolean()
        image = Upload()

    def mutate(self, info, **kwargs):
        user_staff = info.context.user.is_staff
        if user_staff:
            title = kwargs.get("title")
            text = kwargs.get("text")
            breaking = kwargs.get("breaking", False)
            file = kwargs.get("image")
            if file:
                directory = "news"
                path = directory + "/{}/{}/{}/".format(
                    datetime.now().year, datetime.now().month, datetime.now().day
                )
                default_storage.save(path + file.name, ContentFile(file.read()))
            news, created = News.objects.get_or_create(
                defaults={"text": text, "breaking": breaking, "image": file},
                title=title,
            )
            if created:
                if news.breaking:
                    async_to_sync(CHANNEL_LAYER.group_send)(
                        "breaking_news",
                        # {"data": serializers.serialize("json", [news])},
                        {"news_id": news.id},
                    )
                return {"message": "News added", "success": True}
            return {"message": "News already exists", "success": False}
        return {"message": "User not staff", "success": False}


class AddComment(graphene.Mutation):
    """Добавляем комментарий"""

    message = graphene.String()
    success = graphene.Boolean()

    class Arguments:
        text = graphene.String(required=True)
        news_id = graphene.Int(required=True)

    def mutate(self, info, **kwargs):
        news_id = kwargs.get("news_id")
        news = News.objects.get(pk=news_id)
        text = kwargs.get("text")
        user = info.context.user
        comment = Comments.objects.create(news=news, user=user, text=text)
        async_to_sync(CHANNEL_LAYER.group_send)(
            str(news_id),
            {"comment_id": comment.id},
        )
        return {"message": "comment added", "success": True}
