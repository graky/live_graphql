import json
import jwt
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings
from django.urls import path
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from graphql_ws.django.subscriptions import subscription_server
from graphql_ws.constants import WS_PROTOCOL
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser, User
from asgiref.sync import sync_to_async


class MyGraphQLSubscriptionConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.connection_context = None
        if WS_PROTOCOL in self.scope["subprotocols"]:
            cookie = self.scope.get("cookies")
            if "JWT" in cookie:
                JWT = cookie["JWT"]
                sig = jwt.decode(JWT, settings.SECRET_KEY, algorithms=["HS256"])
                username = dict(sig)["username"]
                self.scope["user"] = sync_to_async(User.objects.get)(username=username)
            else:
                self.scope["user"] = sync_to_async(AnonymousUser)()
            self.connection_context = await subscription_server.handle(
                ws=self, request_context=self.scope
            )
            await self.accept(subprotocol=WS_PROTOCOL)
        else:
            await self.close()

    async def disconnect(self, code):
        if self.connection_context:
            self.connection_context.socket_closed = True
            await subscription_server.on_close(self.connection_context)

    async def receive_json(self, content):
        subscription_server.on_message(self.connection_context, content)

    @classmethod
    async def encode_json(cls, content):
        return json.dumps(content)


websocket_urlpatterns = [path("subscriptions", MyGraphQLSubscriptionConsumer.as_asgi())]

auth_application = ProtocolTypeRouter(
    {"websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns))}
)
