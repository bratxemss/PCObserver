import asyncio
import json
from config import defaults


class Client:
    def __init__(self, window):
        self.IP = defaults.IP
        self.Port = defaults.PORT
        self.telegram_id = None
        self.window = window
        self.response = None

    def __repr__(self):
        return f"Connected to {self.IP}:{self.Port}"

    def run_connection(self, message: dict):
        asyncio.run(self.connection(message))

    async def connection(self, message: dict):
        reader, writer = await asyncio.open_connection(self.IP, self.Port)
        message = json.dumps(message).encode()
        writer.write(message)
        await writer.drain()

        while (message := await reader.read(1024)) != b'':
            self.response = message.decode()
            print(self.response)
            try:
                data = json.loads(self.response)
                success = data.get("success")
                if success:
                    print("CONNECTED!")
                else:
                    print("The server does not allow the user")
                    break
            except Exception as ex:
                print(f"Error:{ex}")
                # TODO: write log
        print("Connection closed.")

    def run_answer(self):
        color, message, app = asyncio.run(self.answer())
        return color, message, app

    async def answer(self):
        applications = None
        if self.response:
            data = json.loads(self.response)
            message = data.get("message")
            success = data.get("success")
            try:
                applications = data.get("applications")
            except:
                pass
            if not success:
                color = "#be0000"  # red
            else:
                color = "#33b631"  # green
                if not message:
                    message = "Unexpected error, please restart application"
        else:
            color = "#be0000"  # red
            message = "Server unreachable"
        return color, message, applications


#print(Client(command="connect", data={"user_id": 1}))