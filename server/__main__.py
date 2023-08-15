import asyncio

from . import cfg
from .server import Server


async def main():
    app = Server()
    await app.start_server('127.0.0.1', 8000)


if __name__ == "__main__":
    asyncio.run(main())
