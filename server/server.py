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
                info = []
                information = await Customer.filter(telegram_id=user_id)
                for app in information:
                    info.append({
                        "telegram id": app.telegram_id,
                        "user token": app.user_token,
                        "pc token": app.pc_token,
                    })
                response = {"status": "success", "message": "User login successfully",
                            "Information:": info}
                writer.write(json.dumps(response).encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()

            elif command == "get_info":
                user_id = message.get("data", {}).get("user_id", None)
                if user_id:
                    apps_data = []
                    user_applications = await Application.filter(user=user_id)
                    for app in user_applications:
                        apps_data.append({
                            "id": app.id,
                            "name": app.app_name,
                            "path": app.app_path,
                            "size": app.app_size,
                            "status": app.app_status
                        })
                    if len(apps_data) == 0:
                        response = {"status": "error", "message": "Application list is empty"}
                        writer.write(json.dumps(response).encode())
                    else:
                        response = {"status": "success", "message": "Connected successfully",
                                    "Applications:": apps_data}
                        writer.write(json.dumps(response).encode())
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
                        if not await Application.filter(user=user_id, app_path=app_path).first():
                            await Application.create(
                                user=user_id,
                                app_name=app_name,
                                app_path=app_path,
                                app_size=app_size,
                                app_status=app_status
                            )
                            apps_data = []
                            user_applications = await Application.filter(user=user_id)
                            for app in user_applications:
                                apps_data.append({
                                    "id": app.id,
                                    "name": app.app_name,
                                    "path": app.app_path,
                                    "size": app.app_size,
                                    "status": app.app_status
                                })
                            response = {"status": "success", "message": "Application registered successfully",
                                        "Applications:": apps_data}
                            writer.write(json.dumps(response).encode())
                        else:
                            apps_data = []
                            user_applications = await Application.filter(user=user_id)
                            for app in user_applications:
                                apps_data.append({
                                    "id": app.id,
                                    "name": app.app_name,
                                    "path": app.app_path,
                                    "size": app.app_size,
                                    "status": app.app_status
                                })
                            response = {"status": "error", "message": "Application path is already exist in system",
                                        "Applications:": apps_data}
                            writer.write(json.dumps(response).encode())
                    else:
                        response = {"status": "error", "message": "Invalid application data"}
                        writer.write(json.dumps(response).encode())
                else:
                    response = {"status": "error", "message": "Invalid user_id"}
                    writer.write(json.dumps(response).encode())

                await writer.drain()
                writer.close()
                await writer.wait_closed()

            elif command == "delete_app":
                print("Deleting_app")
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
                        response = {"status": "success" if bool(deleted) else "error", "Application path": app_id}
                    except Exception as e:
                        print("Error occurred during deletion:", e)
                        response = {"status": "error", "message": "An error occurred during deletion."}
                else:
                    response = {"status": "error", "message": "Invalid data."}
                writer.write(json.dumps(response).encode())
                await writer.drain()
                writer.close()
                await writer.wait_closed()
