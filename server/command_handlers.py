import json
import logging
from uuid import uuid4

from asyncio import StreamReader, StreamWriter
from server.models import Customer, Application
from server.utils import get_users_apps

logger = logging.getLogger("commands handlers")


async def send_response(writer, response):
    writer.write(json.dumps(response).encode())
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def register_user(reader: StreamReader, writer: StreamWriter, message):
    user_id = message.get("data", {}).get("user_id", None)
    existing_customer = await Customer.get_or_none(telegram_id=user_id)
    if not existing_customer:
        await Customer.create(
            telegram_id=user_id,
            user_token=str(uuid4()),
            pc_token=str(uuid4())
        )
    info = []
    information = await Customer.select().where(
        Customer.telegram_id == user_id
    )
    for user in information:
        info.append({
            "telegram id": user.telegram_id,
            "user token": user.user_token,
            "pc token": user.pc_token,
        })
    response = {
        "success": True,
        "message": "User login successfully",
        "information": info
    }

    await send_response(writer, response)


async def get_info(reader: StreamReader, writer: StreamWriter, message):
    logger.debug("Get info")
    user_id = message.get("data", {}).get("user_id", None)

    if user_id:
        response = {
            "success": True,
            "message": "Connected successfully",  # I think this message here is incorrect
            "applications": await get_users_apps(user_id)
        }
    else:
        response = {
            "success": False,
            "message": "Incorrect user_id",
        }

    await send_response(writer, response)


async def register_app(reader: StreamReader, writer: StreamWriter, message):
    user_id = message.get("data", {}).get("user_id", None)
    application = message.get("data", {}).get("application", None)

    success = True
    message = None
    if user_id and application:
        app_name = application.get("name", "unknown")
        app_path = application.get("path", "unknown")
        app_size = application.get("size", 0)
        app_status = application.get("status", False)
        if not await Application.select().where(
                Application.user == user_id,
                Application.app_path == app_path
        ).exists():
            await Application.create(
                user=user_id,
                app_name=app_name,
                app_path=app_path,
                app_size=app_size,
                app_status=app_status
            )
            message = "Application registered successfully"
    else:
        success = False
        message = not user_id and "invalid user_id" or "Invalid application data"

    response = {
        "success": success,
        "message": message,
        "applications": await get_users_apps(user_id)
    }

    await send_response(writer, response)


async def delete_app(reader: StreamReader, writer: StreamWriter, message):
    user_id = message.get("data", {}).get("user_id", None)
    app_id = message.get("data", {}).get("application", {}).get("id")
    if user_id and app_id:
        try:
            application = (
                await Application.select()
                .where(
                    Application.id == app_id,
                    Application.user_id == user_id
                )
                .first()
            )
            deleted = await application.delete_instance()
            response = {"success": bool(deleted), "app_id": app_id}
        except Exception as e:
            logger.error("Error occurred during deletion: %s", e)
            response = {"success": False, "message": "An error occurred during deletion."}
    else:
        response = {"success": False, "message": "Invalid data."}

    await send_response(writer, response)
