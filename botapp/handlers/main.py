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
            message.from_user.id,
            f"Hello, {message.from_user.first_name}! I am the test bot 'P.C.Observer'. "
            "My job is to turn on and off the applications on your computer if u want to start "
            "or just print /start")
    )
    return


@Client.on_message(filters.command("start", ["/", ".", "?"]))
async def start(client, message):
    markup = ReplyKeyboardMarkup(
        [
            [KeyboardButton("👋 Начать настройку")],
        ],
        resize_keyboard=True
    )
    asyncio.ensure_future(
        client.send_message(
            message.from_user.id,
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



'''
@Client.on_message(
    filters.text &
    (filters.regex(re.compile(r"^Прикрепить подарочное сообщение$"))
    | filters.regex(re.compile(r"^Изменить номер телефона$"))
    | filters.regex(re.compile(r"^Отправить билет$"))
    | filters.regex(re.compile(r"^Отменить$"))),
    group=1)
async def process_reply_buttons(client, message):
    tgm_id = message.from_user.id

    if message.text == "Изменить номер телефона":
        await client.send_message(
            tgm_id,
            "Пришлите мне исправленный номер телефона.",
            reply_markup=ForceReply()
        )

    elif message.text == "Прикрепить подарочное сообщение":
        await client.send_message(
            tgm_id,
            "Напишите мне сообщение и я отправлю его вместе с билетом.",
            reply_markup=ForceReply()
        )

    elif message.text == "Отправить билет":
        bot.dialogs.register_next_step(tgm_id, make_transfer)
        await bot.dialogs.make_step(tgm_id, client, user, message)

    elif message.text == "Отменить":
        bot.dialogs.clear(tgm_id)
        await client.send_message(
            tgm_id,
            "Отправка билета отменена.",
            reply_markup=ReplyKeyboardRemove()
        )

    return
'''