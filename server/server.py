import asyncio
import json
from asyncio import StreamReader, StreamWriter
from uuid import uuid4

from server.models import Customer, Application


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
                existing_customer = await Customer.get_or_none(telegram_id=user_id)
                if not existing_customer:
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
                    application = message.get("data", {}).get("application", None)
                    if application:
                        app_name = application.get("name", "unknown")
                        app_path = application.get("path", "unknown")
                        app_size = application.get("size", 0)
                        app_status = application.get("status", False)
                        if not await Application.get_or_none(user=user_id) and not await Application.get_or_none(app_path=app_path):
                            await Application.create(
                                user=user_id,
                                app_name=app_name,
                                app_path=app_path,
                                app_size=app_size,
                                app_status=app_status
                            )

                            user_applications = await Application.filter(user=user_id)
                            apps_data = []
                            for app in user_applications:
                                apps_data.append({
                                    "id": app.id,
                                    "name": app.app_name,
                                    "path": app.app_path,
                                    "size": app.app_size,
                                    "status": app.app_status
                                })
                            response = {"status": "success", "message": "Application registered successfully",
                                        "Applications": apps_data}
                            writer.write(json.dumps(response).encode())
                        else:
                            response = {"status": "error", "message": "Application path is already exist in system"}
                            writer.write(json.dumps(response).encode())
                    else:
                        response = {"status": "error", "message": "Invalid application data"}
                        writer.write(json.dumps(response).encode())
                else:
                    response = {"status": "error", "message": "Invalid user_id"}
                    writer.write(json.dumps(response).encode())

                writer.close()
                await writer.wait_closed()

            elif command == "delete_app":
                print("Deleting_app")
                user_id = message.get("data", {}).get("user_id", None)
                if user_id:
                    app_id = (message.get("data", {}).get("application", None))["id"]
                    if app_id:
                        application = await Application.get_or_none(id=app_id)
                        if application:
                            await application.delete()
                            response = {"status": "success", "message": "Application deleted successfully",
                                        "Application path": app_id}
                            writer.write(json.dumps(response).encode())
                        else:
                            response = {"status": "error", "message": "Application not found"}
                            writer.write(json.dumps(response).encode())
                    else:
                        response = {"status": "error", "message": "Invalid application ID"}
                        writer.write(json.dumps(response).encode())
                else:
                    response = {"status": "error", "message": "Invalid user ID"}
                    writer.write(json.dumps(response).encode())

                writer.close()
                await writer.wait_closed()
