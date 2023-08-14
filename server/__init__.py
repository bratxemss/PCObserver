import os

from modconfig import Config
from peewee_aio.manager import Manager


env = os.environ.get("ENV", "defaults")
cfg = Config(f"{__name__}.config.{env}")
db = Manager(cfg.PEEWEE_CONNECTION)
