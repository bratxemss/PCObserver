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
        self.current_response = None

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

        while (message := await self.reader.read(1024)) != b'':
            response = message.decode()
            print(response)
            color, message, apps, command = self.answer(response)
            self.window.process_answer(color=color, message=message)
            try:
                data = json.loads(response)
                success = data.get("success")
                if not success:
                    print("The server does not allow the user")
                    break
                if command:
                    if command == "update_list":
                        self.window.get_application_list(apps)

            except Exception as ex:
                print(f"Error:{ex}")
            return
                # TODO: write log
        print("Connection closed.")


    def send_message(self, message: dict):
        self.writer.write(json.dumps(message).encode())
        asyncio.run(self.writer.drain())

    def answer(self, response):
        applications = None
        command = None
        if response:
            data = json.loads(response)
            message = data.get("message")
            success = data.get("success")
            try:
                applications = data.get("applications")
                if applications:
                    command = "update_list"
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
        return color, message, applications,command


#print(Client(command="connect", data={"user_id": 1}))