import asyncio
import re

from pyrogram import Client, filters
from pyrogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from .utils import (
    get_application_data,
    get_token,
    connect_to_pc,
    dynamic_data_filter,

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
        buttons = []
        message, buttons_info = await connect_to_pc(gm_id)
        for app in buttons_info["applications"]:
            print(app)
            app_name = app.get("name")
            app_path = app.get("path")
            button = [InlineKeyboardButton(app_name, callback_data=f"app_{gm_id}:%%:{app_path}")]
            buttons.append(button)

        keyboard = InlineKeyboardMarkup(buttons)
        await client.send_message(
            gm_id,
            message,
            reply_markup=keyboard
        )

    return


@Client.on_callback_query(dynamic_data_filter(r"app_"))
async def send_app_info(client, callback_query):
    callback_data = callback_query.data
    items = str(callback_data.replace("app_", "")).split(":%%:")
    application_data = await get_application_data(items[0], items[1])
    await callback_query.message.reply_text(f"{application_data}")
    await callback_query.answer()
