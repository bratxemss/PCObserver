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
    send_request_to_customer
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
            [KeyboardButton("✅ Connect to PC ✅")],
            [KeyboardButton("🎶 Set up sound 🎶")]
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
            | filters.regex(re.compile(r"^🎶 Set up sound 🎶$"))

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
                if app.get("favorite"):
                    button = [InlineKeyboardButton(f"{app_name}⭐️", callback_data=f"app_/{gm_id}/{app_id}")]
                else:
                    button = [InlineKeyboardButton(f"{app_name}", callback_data=f"app_/{gm_id}/{app_id}")]
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
    elif message.text == "🎶 Set up sound 🎶":
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"Volume up", callback_data=f"Volume_up/{gm_id}")],
                                         [InlineKeyboardButton(f"Volume down", callback_data=f"Volume_down/{gm_id}")]])
        message = "🎶 Volume settings 🎶"
        await client.send_message(
            gm_id,
            message,
            reply_markup=keyboard
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


@Client.on_callback_query(dynamic_data_filter(r"^(ON_|OFF_)/[0-9]+/[0-9]+$"))
async def turn_app(client, callback_query):
    callback_data = callback_query.data
    command, user_id, app_id = callback_data.split("/")
    message = await send_request_to_customer(user_id, app_id=app_id, command=f"{command}")
    await callback_query.message.reply_text(f"{message}")
    await callback_query.answer()


@Client.on_callback_query(dynamic_data_filter(r"^(Volume_up|Volume_down)/[0-9]+$"))
async def turn_app_sound(client, callback_query):
    callback_data = callback_query.data
    command, user_id = callback_data.split("/")
    message = await send_request_to_customer(user_id, app_id=None, command=f"{command}")
    if "✅" in message:
        await callback_query.answer()
    elif "✅" not in message:
        await callback_query.message.reply_text(f"{message}")
        await callback_query.answer()
