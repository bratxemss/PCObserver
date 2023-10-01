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
    send_turning_request
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
        if buttons_info["applications"]:
            for app in buttons_info["applications"]:
                app_name = app.get("name")
                app_id = app.get("id")
                button = [InlineKeyboardButton(app_name, callback_data=f"app_/{gm_id}/{app_id}")]
                buttons.append(button)

            keyboard = InlineKeyboardMarkup(buttons)
            await client.send_message(
                gm_id,
                message,
                reply_markup=keyboard
            )
        else:
            await client.send_message(
                gm_id,
                message,
            )

    return


@Client.on_callback_query(dynamic_data_filter(r"^app_/[0-9]+/[0-9]+$"))
async def send_app_info(client, callback_query):
    callback_data = callback_query.data
    _, user_id, app_id = callback_data.split("/")
    application_data = await get_application_data(user_id, app_id)
    buttons = [InlineKeyboardButton("On🌝", callback_data=f"ON_/{user_id}/{app_id}"),
               InlineKeyboardButton("Off🌚", callback_data=f"OFF_/{user_id}/{app_id}")]
    keyboard = InlineKeyboardMarkup([buttons])
    await callback_query.message.reply_text(f"{application_data}", reply_markup=keyboard)
    await callback_query.answer()


@Client.on_callback_query(dynamic_data_filter(r"^ON_/[0-9]+/[0-9]+$"))
async def turn_on_app(client,callback_query):
    callback_data = callback_query.data
    _, user_id, app_id = callback_data.split("/")
    message = await send_turning_request(user_id, app_id, command="On")
    print(message)
    await callback_query.message.reply_text(f"{message}")
    await callback_query.answer()


@Client.on_callback_query(dynamic_data_filter(r"^OFF_/[0-9]+/[0-9]+$"))
async def turn_off_app(client,callback_query):
    callback_data = callback_query.data
    _, user_id, app_id = callback_data.split("/")
    message = await send_turning_request(user_id, app_id, command="Off")
    print(message)
    await callback_query.message.reply_text(f"{message}")
    await callback_query.answer()