import asyncio
import re

from pyrogram import Client, filters
from pyrogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)


@Client.on_message(filters.command("help", ["/", ".", "?"]))
async def helper(client, message):
    asyncio.ensure_future(
        client.send_message(
            message.chat.id,
            f"Hello, {message.from_user.first_name}! I am the test bot 'P.C.Observer'. "
            "My job is to turn on and off the applications on your computer if u want to start "
            "or just print /start")
    )
    return


@Client.on_message(filters.command("start", ["/", ".", "?"]))
def start(client, message):
    markup = ReplyKeyboardMarkup(
        [
            [KeyboardButton("👋 Начать настройку")],
        ],
        resize_keyboard=True
    )
    asyncio.ensure_future(
        client.send_message(
            message.chat.id,
            text=f"Hello, {message.from_user.first_name}! I am the test bot 'P.C.Observer'. "
                 "My job is to turn on and off the "
                 "applications on your computer",
            reply_markup=markup
        )
    )
    return


@Client.on_message(
    filters.text &
    (
        filters.regex(re.compile(r"^👋 Начать настройку$"))
        | filters.regex(re.compile(r"^🫡 Создать Токен$"))
    ),
    group=1)
async def process_operations(client, message):
    pass
