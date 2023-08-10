import asyncio
import json


async def main():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8000)
    message = {
        "command": "delete_app",
        "data": {"user_id": 6174434600, "application": {"id": 1}}
    }
    message = json.dumps(message).encode()
    writer.write(message)
    await writer.drain()

    while (message := await reader.read(1024)) != b'':
        print(message.decode())

    print("Connection closed.")


asyncio.run(main())
