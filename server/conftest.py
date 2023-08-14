import asyncio
import json
import pytest

from server.server import Server


async def server_starter(port):
    server = Server()
    await server.start_server('127.0.0.1', port)


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
    """
    Send message to test server.

    :param port: port equal server fixture result
    :param message: str or dict message for test server.
    :return:
    """

    return TestClient(server)
