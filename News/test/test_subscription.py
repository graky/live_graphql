import textwrap
import pytest
from main.schema import Query, Mutation, Subscription


@pytest.mark.asyncio
async def test_main_usecase(gql):
    client = gql(
        query=Query,
        mutation=Mutation,
        subscription=Subscription,
        consumer_attrs={"strict_ordering": True},
    )
    await client.connect_and_init()
    # подписываемся на срочные новости
    sub_id = await client.send(
        msg_type="start",
        payload={
            "query": textwrap.dedent(
                """
                subscription NewsSubscription {
  breaking_news {
    news_id
    news_title
  }
}

                """
            ),
        },
    )

    await client.assert_no_messages()
    # создаем срочную новость
    msg_id = await client.send(
        msg_type="start",
        payload={
            "query": textwrap.dedent(
                """
                mutation AddNews{
                add_news(
                    text: "some text"
                    title: "Breaking News!"
                    breaking: true
                )
                {
                    message
                    success
                }
            }
                """
            ),
        },
    )

    # проверка на добавление новости
    resp = await client.receive(assert_id=msg_id, assert_type="data")
    assert resp["data"] == {"add_news": {"message": "News added", "success": True}}
    await client.receive(assert_id=msg_id, assert_type="complete")

    # проверяем, пришло ли уведомление по срочной новости
    resp = await client.receive(assert_id=sub_id, assert_type="data")
    event = resp["data"]
    assert event == {"breaking_news": {"news_id": 1, "news_title": "Breaking News!"}}
    await client.finalize()
