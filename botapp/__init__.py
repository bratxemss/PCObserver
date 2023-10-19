import asyncio
import json
import os

# import uvloop
from pyrogram import Client
from modconfig import Config


class ClientForServer:
    def __init__(self, host, port):
        self.IP = host
        self.Port = port

    def __repr__(self):
        return f"Info: connected to {self.IP}:{self.Port}"

    async def send_message(self, command, data):
        reader, writer = await asyncio.open_connection(self.IP, self.Port)
        message = {
            "command": command,
            "data": data
        }
        message = json.dumps(message).encode()
        writer.write(message)
        await writer.drain()
        response = (await reader.read(1024)).decode()
        writer.close()
        await writer.wait_closed()
        return response


class Bot(Client):
    def __init__(self, env=None):
        env = env or os.environ.get("ENV", "develop")
        self.cfg = Config(f"{__name__}.config.{env}")
        self.ENV = env
        self.servers_client = ClientForServer(self.cfg.SERVER_HOST, self.cfg.SERVER_PORT)

        super().__init__(
            self.cfg.TELEGRAM_BOT_NAME,
            bot_token=self.cfg.PYROGRAM_BOT_TOKEN,
            api_id=self.cfg.TELEGRAM_API_ID,
            api_hash=self.cfg.TELEGRAM_API_HASH,
            plugins=dict(root="botapp/handlers")
        )



bot = Bot()
