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
            print("message:", message)
            try:
                data = json.loads(response)
            except:  # noqa
                # TODO: write log
                self.window.process_answer({"success": False, "message": "Invalid response from server!"})
                break

            if not logged_in:
                if data.get("success"):
                    self.window.window.after(1, lambda: self.window.change_window())
                self.window.process_answer(data)
                if "applications" in data:
                    self.window.set_functional(apps=data["applications"], telegram_id=self.telegram_id)
                logged_in = True

            if "applications" in data:
                self.window.render_applications(data["applications"])

        print("Connection closed.")
        return

    async def send_message(self, message: dict):
        self.writer.write(json.dumps(message).encode())
        await self.writer.drain()

#print(Client(command="connect", data={"user_id": 1}))
