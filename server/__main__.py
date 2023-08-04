import asyncio

from server.server import Server


async def main():
    server = Server()
    await server.start_server('127.0.0.1', 8000)


if __name__ == "__main__":
    asyncio.run(main())
