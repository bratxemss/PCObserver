import asyncio
import json
import time

from config import defaults


class Client:
    def __init__(self, window):
        self.IP = defaults.IP
        self.Port = defaults.PORT
        self.telegram_id = None
        self.window = window
        self.reader = None
        self.writer = None
        self.current_response = None

    def __repr__(self):
        return f"Connected to {self.IP}:{self.Port}"

    def run_connection(self):
        asyncio.run(self.connection())

    async def connection(self):
        self.reader, self.writer = await asyncio.open_connection(self.IP, self.Port)
        self.send_message({
            "command": "connect",
            "data": {"user_id": self.telegram_id}
        })
        logged_in = False
        while (message := await self.reader.read(1024)) != b'':
            response = message.decode()
            print(response)
            try:
                data = json.loads(response)
            except:  # noqa
                # TODO: write log
                self.window.process_answer({"success": False, "message": "Invalid response from server!"})
                break

            if not logged_in:
                if data.get("success"):
                    self.window.window.after(1, lambda: self.window.change_window())  # отрисовка интерфейса в основном потоке
                    if "applications" in data:
                        time.sleep(1)
                        self.window.render_applications(data["applications"])
                    self.window.set_functional(data["applications"], telegram_id=self.telegram_id)
                    logged_in = True
                self.window.process_answer(data)

        print("Connection closed.")
        return

    def send_message(self, message: dict):
        self.writer.write(json.dumps(message).encode())
        asyncio.create_task(self.writer.drain())

#print(Client(command="connect", data={"user_id": 1}))