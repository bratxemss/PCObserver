import asyncio
import json


class Client(asyncio.Protocol):
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        server_message = '{!r}'.format(data.decode())
        print(f"Data received: {server_message}")

    def connection_lost(self, exc):
        print('The server closed the connection')
        self.on_con_lost.set_result(True)


async def main():
    # Получаем ссылку на цикл событий, т.к. планируем
    # использовать низкоуровневый API.
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()
    import uuid

    # message = {
    #     "command": "register_app",
    #     "data":
    #         {
    #             "user_id": 1235641635,
    #             "application": {
    #                 "name": "Doom 2016",
    #                 "path": "C:/Users/bratx/Desktop/Bread & Fred Demo.url",
    #                 "size": 202,
    #                 "status": True,
    #             }
    #         }
    # }
    message1 = {
        "command": "delete_app",
        "data":
            {
                "user_id": 1235641635,
                "application": {
                    "id": 1,
                }
            }
    }
    message = json.dumps(message1)
    transport, protocol = await loop.create_connection(
        lambda: Client(message, on_con_lost),
        '127.0.0.1', 8000)

    # Ждем, пока протокол не подаст сигнал о том,
    # что соединение потеряно, далее закроем транспорт.
    try:
        await on_con_lost
    finally:
        transport.close()

asyncio.run(main())
