import asyncio
import json
from config import defaults


class Client:
    def __init__(self, window):
        self.IP = defaults.IP
        self.Port = defaults.PORT
        self.telegram_id = None
        self.window = window
        self.reader = None
        self.writer = None

    def __repr__(self):
        return f"Connected to {self.IP}:{self.Port}"

    def run_connection(self):
        asyncio.run(self.connection())

    async def connection(self):
        self.reader, self.writer = await asyncio.open_connection(self.IP, self.Port)
        message = json.dumps({
            "command": "connect",
            "data": {"user_id": self.telegram_id}
        }).encode()
        self.writer.write(message)
        await self.writer.drain()

        logged_in = False

        while (message := await self.reader.read(1024)) != b'':
            response = message.decode()
            try:
                data = json.loads(response)
            except:  # noqa
                self.window.process_answer({"success": False, "message": "Invalid response from server!"})
                self.window.logger.warning("Invalid response from server!")
                break

            if not logged_in:
                if data.get("success"):
                    self.window.window.after(1, lambda: self.window.change_window())
                self.window.process_answer(data)
                if "applications" in data:
                    self.window.set_functional(apps=data["applications"], telegram_id=self.telegram_id)
                    for i in data["applications"]:
                        if i["favorite"]:
                            self.window.favorite_list.append(i)
                logged_in = True
            if "command" in data:
                if logged_in:
                    command = data.get("command")
                    app_id = data.get("data", {}).get("app_id", None)
                    if command == "ON_":
                        self.window.turn_application(app_id=app_id, command=command)
                    elif command == "OFF_":
                        self.window.turn_application(app_id=app_id, command=command)
                    elif command == "Volume_up":
                        self.window.set_volume(command=command)
                    elif command == "Volume_down":
                        self.window.set_volume(command=command)

            if "applications" in data:
                self.window.render_applications(data["applications"],label=self.window.list_of_apps)
                self.window.apps = data["applications"]
                self.window.render_applications(self.window.favorite_list, label=self.window.list_of_favorite_apps)

        self.window.logger.warning("Connection closed")
        return

    async def send_message(self, message: dict):
        self.writer.write(json.dumps(message).encode())
        await self.writer.drain()

#print(Client(command="connect", data={"user_id": 1}))
