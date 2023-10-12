import asyncio

import pytest
from unittest import mock

from pyrogram.types.user_and_chats.user import User


@pytest.fixture(scope='session')
def loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def bot():
    from botapp import bot
    bot.me = User(id=5454227880, is_self=True, is_bot=True, username="UN")
    bot.is_connected = True
    return bot


@pytest.fixture
def tg_user():
    return User(
        id=238322888,
        is_bot=False,
        is_self=False,
        first_name="Eugene",
        username="fake_user"
    )


@pytest.fixture
def send_message():
    async def response():
        return True
    with mock.patch("botapp.Bot.send_message") as mocked:
        mocked.return_value = response()
        yield mocked


@pytest.fixture
async def server_client():
    from botapp import bot

    async def response():
        return {}

    with mock.patch("botapp.bot.servers_client.send_message") as mocked:
        mocked.return_value = response()
        yield mocked


