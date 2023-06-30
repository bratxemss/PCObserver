import os

import uvloop
from peewee_aio.manager import Manager
from pyrogram import Client
from modconfig import Config


class Bot(Client):
    def __init__(self, env=None):
        env = env or os.environ.get("ENV", "develop")
        self.cfg = Config(f"{__name__}.config.{env}")
        self.ENV = env
        self.db = Manager(self.cfg.PEEWEE_CONNECTION)

        super().__init__(
            self.cfg.TELEGRAM_BOT_NAME,
            bot_token=self.cfg.PYROGRAM_BOT_TOKEN,
            api_id=self.cfg.TELEGRAM_API_ID,
            api_hash=self.cfg.TELEGRAM_API_HASH,
            plugins=dict(root="botapp/handlers")
        )


uvloop.install()

bot = Bot()
