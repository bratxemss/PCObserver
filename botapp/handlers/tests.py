from pyrogram.types import Message
from pyrogram.types.messages_and_media.message import Str

from .main import start


async def test_start(bot, send_message, tg_user):
    message = Message(text=Str("/start"), id=1, from_user=tg_user)

    await start(bot, message)
    assert send_message.called

    user_id = send_message.call_args.args[0]
    assert user_id == tg_user.id
    kwargs = send_message.call_args.kwargs
    text = kwargs["text"]
    assert text == (f"Hello, {tg_user.first_name}! I am the test bot 'P.C.Observer'. "
                    "My job is to turn on and off the "
                    "applications on your computer")
    assert "reply_markup" in kwargs
    keyboard = kwargs["reply_markup"].keyboard
    assert len(keyboard) == 2
    assert keyboard[0][0].text == '🫡 Create Token'
    assert keyboard[1][0].text == '✅ Connect to PC ✅'
