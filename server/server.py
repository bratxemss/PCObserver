import asyncio
import json
import logging
import pytest
from server.models import Customer
from asyncio import StreamReader, StreamWriter

from server.command_handlers import (
    register_user,
    get_info,
    get_application_info,
    register_app,
    delete_app,
    send_response
)

logging.basicConfig(filemode="console", encoding="utf-8", level=logging.DEBUG)
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

    async def client_connected(self, reader: StreamReader, writer: StreamWriter):
        message = await reader.read(1024)
        logger.info("Message: %s", message.decode())
        message = json.loads(message)

        command = message.get("command", None)

        if command:
            if command == "register_user":
                await register_user(reader, writer, message)

            elif command == "get_info":
                await get_info(reader, writer, message)

            elif command == "get_application_info":
                await get_application_info(reader, writer, message)

            elif command == "connect":
                user_id = message.get("data", {}).get("user_id", None)
                existing_customer = await Customer.get_or_none(telegram_id=user_id)
                if existing_customer:
                    self.users[str(user_id)] = {"reader": reader, "writer": writer}
                    success = True
                    message = "Connected successfully"
                    logger.info(
                        "New client connection: %s. Number of connected clients = %s",
                        user_id, len(self.users))

                else:
                    success = False
                    message = "Wrong telegram ID"
                response = {
                    "success": success,
                    "message": message
                }
                await send_response(writer, response)

            elif command == "send_command":
                logger.debug("NEW COMMAND %s", message)
                data = message.get("data", {})
                user_id = str(data.get("user_id", None))
                if user_id:
                    user_writer = self.users[user_id]["writer"]
                    await send_response(user_writer, data, close_conn=False)
                writer.close()
                await writer.wait_closed()

            elif command == "register_app":
                await register_app(reader, writer, message)

            elif command == "delete_app":
                await delete_app(reader, writer, message)

        else:
            await send_response(writer, {"success": False, "message": "Command not found."})
