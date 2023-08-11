import asyncio
import re

from pyrogram import Client, filters
from pyrogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton

)

from .utils import get_token, connect_to_pc, dynamic_data_filter


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
            [KeyboardButton("🫡 Create Token")],
            [KeyboardButton("✅ Connect to PC ✅")]
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
        filters.regex(re.compile(r"^🫡 Create Token$"))
        | filters.regex(re.compile(r"^✅ Connect to PC ✅$"))
    ),
    group=1)
async def process_operations(client, message):
    gm_id = message.from_user.id
    if message.text == "🫡 Create Token":
        await client.send_message(
            gm_id,
            await get_token(gm_id),
        )
    elif message.text == "✅ Connect to PC ✅":
        button_row = []
        apps_info, process_info = await connect_to_pc(gm_id)
        for item in apps_info["Applications"]:
            row = [InlineKeyboardButton(item["name"], callback_data=f"app_{item['path'],item['size']}")]
            button_row.append(row)
        markup = InlineKeyboardMarkup(button_row)
        await client.send_message(
            gm_id,
            process_info,
            reply_markup=markup
        )
    return


@Client.on_callback_query(dynamic_data_filter(r"app_"))
async def send_app_info(client, callback_query):
    callback_data = callback_query.data
    item_name = callback_data.replace("app_", "")
    await callback_query.message.reply_text(f"You clicked: {item_name}")
    await callback_query.answer()