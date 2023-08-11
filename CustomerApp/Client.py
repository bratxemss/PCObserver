import asyncio
import json
from config import defaults

class Client():
    def __init__(self, command=None, data=None):
        if data is None:
            data = {}
        if command is None:
            command = {}
        self.command = command
        self.data = data
        self.IP = defaults.IP
        self.Port = defaults.PORT
        asyncio.run(self.connection())

    def __repr__(self):
        return f"Info:{self.command, self.data} to {self.IP}:{self.Port}"

    async def connection(self):
        reader, writer = await asyncio.open_connection(self.IP, self.Port)
        message = {
            "command": self.command,
            "data": self.data
        }
        message = json.dumps(message).encode()
        writer.write(message)
        await writer.drain()
        while (message := await reader.read(1024)) != b'':
            print(message.decode())
        print("Connection closed.")



#print(Client(command="connect", data={"user_id": 1}))