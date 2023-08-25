import asyncio
import json
import pytest

from .server import Server


async def server_starter(port):
    app = Server()
    await app.start_server('127.0.0.1', port)


@pytest.fixture()
def server(event_loop, unused_tcp_port):
    cancel_handle = asyncio.ensure_future(
        server_starter(unused_tcp_port),
        loop=event_loop
    )
    event_loop.run_until_complete(asyncio.sleep(0.01))

    try:
        yield unused_tcp_port
    finally:
        cancel_handle.cancel()


class TestClient:
    def __init__(self, server):
        self.server_port = server

    async def send_message(self, message: str or dict) -> str:
        reader, writer = await asyncio.open_connection('127.0.0.1', self.server_port)

        writer.write(json.dumps(message).encode())
        await writer.drain()
        result = await reader.read()

        return json.loads(result.decode())


@pytest.fixture()
def client(server):
    return TestClient(server)


@pytest.fixture(autouse=True)
async def db(server):
    from . import db
    await db.create_tables()
    yield db
    await db.drop_tables()
    await db.disconnect()

