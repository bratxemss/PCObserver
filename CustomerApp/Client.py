import asyncio
import json
from config import defaults


class Client:
    def __init__(self, window):
        self.IP = defaults.IP
        self.Port = defaults.PORT
        self.telegram_id = None
        self.window = window

    def __repr__(self):
        return f"Connected to {self.IP}:{self.Port}"

    def run_connection(self):
        asyncio.run(self.connection())

    async def connection(self):
        reader, writer = await asyncio.open_connection(self.IP, self.Port)
        message = {
            "command": "connect",
            "data": {"user_id": self.telegram_id}
        }
        message = json.dumps(message).encode()
        writer.write(message)
        await writer.drain()
        print("CONNECTED!")

        while (message := await reader.read(1024)) != b'':
            message = message.decode()
            print(message)
            try:
                data = json.loads(message)
                command = data.get("client_command")
                if command["action"] == "change_label_login":
                    column = command.get("column")
                    self.window.label_login.grid(row=0, column=column, padx=5, pady=5, sticky="n")
                    self.window.window.update()
            except Exception as ex:
                print(f"ERROR: {ex}")
                # TODO: write log
                pass
        print("Connection closed.")



#print(Client(command="connect", data={"user_id": 1}))