import json
import logging

from asyncio import StreamReader, StreamWriter
from server.models import Customer, Application

logger = logging.getLogger("commands handlers")


async def send_response(writer, response, close_conn=True):
    writer.write(json.dumps(response).encode())
    await writer.drain()
    if close_conn:
        writer.close()
        await writer.wait_closed()


async def register_user(reader: StreamReader, writer: StreamWriter, message):
    user_id = message.get("data", {}).get("user_id", None)
    user = await Customer.get_or_none(telegram_id=user_id)
    if not user:
        user = await Customer.create_with_telegram_id(user_id)
    info = {
            "telegram_id": user.telegram_id,
            "user_token": user.user_token,
            "pc_token": user.pc_token,
    }
    response = {
        "success": True,
        "message": "User registered successfully",
        "data": info
    }

    await send_response(writer, response)


async def get_info(reader: StreamReader, writer: StreamWriter, message):
    logger.debug("Get info")
    user_id = message.get("data", {}).get("user_id", None)
    apps = []
    if user_id:
        apps = await Application.get_apps_by_user(user_id)
        if apps:
            success = True
            message = "Connected successfully"
        else:
            success = False
            message = "Application list is empty"
    else:
        success = False
        message = "Incorrect user ID"
    response = {
        "success": success,
        "message": message,
        "applications": apps
    }
    await send_response(writer, response)


async def get_application_info(reader: StreamReader, writer: StreamWriter, message):
    user_id = message.get("data", {}).get("user_id", None)
    app_id = message.get("data", {}).get("app_id", None)
    logger.debug(f"Get app info about user {user_id}")
    app_info = []
    if user_id and app_id:
        app_info = await Application.get_app_by_id(user_id, app_id)
        if app_info:
            success = True
            message = "Application information found successfully"
        else:
            success = False
            message = f"Application cant found information about application"
    else:
        success = False
        message = "The user does not exist or the application path is incorrect"

    response = {
        "success": success,
        "message": message,
        "information": app_info
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
        app_favorite = application.get("favorite", False)
        if not await Application.select().where(
                Application.user == user_id,
                Application.app_path == app_path
        ).exists():
            await Application.create(
                user=user_id,
                app_name=app_name,
                app_path=app_path,
                app_size=app_size,
                app_status=app_status,
                app_favorite=app_favorite,
            )
            message = "Application registered successfully"
    else:
        success = False
        message = not user_id and "invalid user_id" or "Invalid application data"

    response = {
        "success": success,
        "message": message,
        "applications": await Application.get_apps_by_user(user_id)
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
            response = {"success": bool(deleted), "message": "Deleted successfully", "app_id": app_id}
        except Exception as e:
            logger.error("Error occurred during deletion: %s", e)
            response = {"success": False, "message": "An error occurred during deletion."}
    else:
        response = {"success": False, "message": "Invalid data."}

    await send_response(writer, response)
