import asyncio
import inspect
import sys
import threading
import re
import channels
import django
import graphene
import pytest
from django.urls import re_path
import channels_graphql_ws
import channels_graphql_ws.testing


@pytest.fixture
def event_loop(request):
    del request
    if sys.platform == "win32" and sys.version_info.minor >= 8:
        asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy()  # pylint: disable=no-member
        )
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def gql(db, request):
    del db

    issued_clients = []

    def client_constructor(
        *,
        query=None,
        mutation=None,
        subscription=None,
        consumer_attrs=None,
        communicator_kwds=None,
    ):
        class ChannelsConsumer(channels_graphql_ws.GraphqlWsConsumer):

            schema = graphene.Schema(
                query=query,
                mutation=mutation,
                subscription=subscription,
                auto_camelcase=False,
            )

        # Set additional attributes to the `ChannelsConsumer`.
        if consumer_attrs is not None:
            for attr, val in consumer_attrs.items():
                setattr(ChannelsConsumer, attr, val)

        application = channels.routing.ProtocolTypeRouter(
            {
                "websocket": channels.routing.URLRouter(
                    [
                        re_path(r"wsgraphql", ChannelsConsumer.as_asgi()),
                    ]
                )
            }
        )

        transport = channels_graphql_ws.testing.GraphqlWsTransport(
            application=application,
            path="wsgraphql/",
            communicator_kwds=communicator_kwds,
        )

        client = channels_graphql_ws.testing.GraphqlWsClient(transport)
        issued_clients.append(client)
        return client

    yield client_constructor

    # Assert all issued client are properly finalized.
    for client in reversed(issued_clients):
        assert (
            not client.connected
        ), f"Test has left connected client: {request.node.nodeid}!"


@pytest.fixture(scope="session", autouse=True)
def synchronize_inmemory_channel_layer():
    guard = threading.RLock()

    def wrap(func):
        if inspect.iscoroutinefunction(func):

            async def wrapper(*args, **kwds):
                with guard:
                    return await func(*args, **kwds)

        else:

            def wrapper(*args, **kwds):
                with guard:
                    return func(*args, **kwds)

        return wrapper

    callables_to_protect = [
        "_clean_expired",
        "_remove_from_groups",
        "close",
        "flush",
        "group_add",
        "group_discard",
        "group_send",
        "new_channel",
        "send",
    ]
    for attr_name in callables_to_protect:
        setattr(
            channels.layers.InMemoryChannelLayer,
            attr_name,
            wrap(getattr(channels.layers.InMemoryChannelLayer, attr_name)),
        )
