import asyncio
from asyncio import StreamReader, StreamWriter
import json
import logging

from server.command_handlers import (
    register_user,
    get_info,
    register_app,
    delete_app
)


logger = logging.getLogger("server")


class Server:
    def __init__(self):
        self.users = {}

    async def start_server(self, host: str, port: int):
        server = await asyncio.start_server(self.client_connected, host, port)

        async with server:
            await server.serve_forever()

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

            elif command == "connect":
                user_id = message.get("data", {}).get("user_id", None)
                if user_id:
                    self.users[user_id] = {"reader": reader, "writer": writer}
                logger.info(
                    "New client connection: %s. Number of connected clients = %s",
                    user_id, len(self.users))

            elif command == "send_command":
                data = message.get("data", {})
                user_id = data.get("user_id", None)
                if user_id:
                    user_writer = self.users[user_id]["writer"]
                    user_writer.write(json.dumps(data).encode())
                    await user_writer.drain()
                    writer.close()
                    await writer.wait_closed()

            elif command == "register_app":
                await register_app(reader, writer, message)

            elif command == "delete_app":
                await delete_app(reader, writer, message)
