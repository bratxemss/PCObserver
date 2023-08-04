import asyncio
import json
from asyncio import StreamReader, StreamWriter
from uuid import uuid4

from server.models import Customer


class Server:
    def __init__(self):
        self.users = {}

    async def start_server(self, host: str, port: int):
        server = await asyncio.start_server(self.client_connected, host, port)

        async with server:
            await server.serve_forever()

    async def client_connected(self, reader: StreamReader, writer: StreamWriter):
        print("Connected new")
        message = await reader.read(1024)
        message = json.loads(message)
        print("Message", message)

        command = message.get("command", None)
        if command:
            if command == "register_user":
                user_id = message.get("data", {}).get("user_id", None)
                # TODO: проверять пользователя на существование
                await Customer.create(
                    telegram_id=user_id,
                    user_token=str(uuid4()),
                    pc_token=str(uuid4())
                )
                writer.close()
                await writer.wait_closed()

            elif command == "connect":
                user_id = message.get("data", {}).get("user_id", None)
                if user_id:
                    self.users[user_id] = {"reader": reader, "writer": writer}
                print(self.users)

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
                '''регистрируем новое управляемое приложение'''
                print("Register_app")
                user_id = message.get("data", {}).get("user_id", None)
                if user_id:
                    pass
                    # создать запись о приложении в таблице Application
                    # после создания записи о приложении отправить список приложений в ответ
                writer.close()
                await writer.wait_closed()
            elif command == "delete_app":
                pass
