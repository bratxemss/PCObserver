import asyncio
import json
import logging
import pytest
from server.models import Customer, Application
from asyncio import StreamReader, StreamWriter

from server.command_handlers import (
    register_user,
    get_info,
    get_application_info,
    register_app,
    delete_app,
    send_response,
    turn,
    add_to_favorite,
    remove_from_favorite
)

logging.basicConfig(filemode="console", encoding="utf-8", level=logging.INFO)
logger = logging.getLogger("server")


class Server:
    def __init__(self):
        self.users = {}

    async def start_server(self, host: str, port: int):
        server = await asyncio.start_server(self.client_connected, host, port)

        try:
            async with server:
                await server.serve_forever()
        except pytest.PytestUnraisableExceptionWarning:
            pass

    @staticmethod
    async def _listen_messages(reader, writer, user_id):
        while (data := await asyncio.wait_for(reader.read(1024), 3600)) != b'':
            message = json.loads(data.decode())
            logger.info("Message: %s", message)

            command = message.get("command", None)
            if command:
                # process commands from client
                if command == "get_info":
                    await get_info(reader, writer, message)

                elif command == "test":
                    await send_response(
                        writer,
                        {"SUCCESS": True, "data": {"user_id": "TESTED ID"}},
                        close_conn=False
                    )

                elif command == "get_application_info":
                    await get_application_info(reader, writer, message)

                elif command == "register_app":
                    await register_app(reader, writer, message)

                elif command == "delete_app":
                    await delete_app(reader, writer, message)

                elif command == "add_to_favorite":
                    await add_to_favorite(reader, writer, message)

                elif command == "remove_from_favorite":
                    await remove_from_favorite(reader, writer, message)

    async def client_connected(self, reader: StreamReader, writer: StreamWriter):
        message = await reader.read(1024)
        logger.info("Message: %s", message.decode())
        message = json.loads(message)

        user_id = message.get("data", {}).get("user_id", None)
        if not user_id:
            await send_response(writer, {"success": False, "message": "User_id is missing."})
            return

        command = message.get("command", None)
        if command:
            # process commands from bot
            if command == "register_user":
                await register_user(reader, writer, message)
            elif command == "get_info":
                await get_info(reader, writer, message)
            elif command == "get_application_info":
                await get_application_info(reader, writer, message)
            elif command == "turn":
                await turn(reader, writer, message, self.users)
            elif command == "connect":
                if not await Customer.get_or_none(telegram_id=user_id):
                    await Customer.create_with_telegram_id(user_id)

                self.users[str(user_id)] = {"writer": writer}
                logger.info(
                    "New client connection: %s. Number of connected clients = %s",
                    user_id,
                    len(self.users)
                )

                asyncio.create_task(self._listen_messages(reader, writer, user_id))

                response = {
                    "success": True,
                    "message": "Connected successfully",
                    "applications": await Application.get_apps_by_user(user_id)
                }
                await send_response(writer, response, close_conn=False)

            elif command == "send_command":
                logger.debug("NEW COMMAND %s", message)
                data = message.get("data", {})
                user_id = str(data.get("user_id", None))
                if user_id:
                    user_writer = self.users[user_id]["writer"]
                    await send_response(user_writer, data, close_conn=False)
                writer.close()
                await writer.wait_closed()
        else:
            await send_response(writer, {"success": False, "message": "Command not found."})
