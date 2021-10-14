import channels_graphql_ws

import channels
import channels.auth
import django.core.asgi
from main.schema import schema
from django.urls import re_path


class MyGraphqlWsConsumer(channels_graphql_ws.GraphqlWsConsumer):
    """Channels WebSocket consumer which provides GraphQL API."""

    schema = schema


application = channels.routing.ProtocolTypeRouter({
    "websocket": channels.routing.URLRouter([re_path(r"wsgraphql", MyGraphqlWsConsumer.as_asgi()),
    ])
})
