import json
import asyncio
import re
from pyrogram import filters


class Connections:
    def __init__(self, command, data):
        self.command = command
        self.data = data
        self.IP = '127.0.0.1'
        self.Port = 8000

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
        response = (await reader.read(1024)).decode()
        writer.close()
        await writer.wait_closed()
        return response


async def reader(message: dict, unexpected_info_need=True) -> str:
    unexpected_info = []
    answer = ""
    if message.get("message"):
        answer += f"{message['message']}! "
    if message.get("status"):
        if message.get("status") == "success":
            answer = "✅ " + answer + "✅"
        elif message.get("status") == "error":
            answer = "❌ " + answer + "❌"
    if unexpected_info_need:
        for item, key in message.items():
            if not item == "message" and not item == "status":
                if isinstance(key, list):
                    for app in key:
                        if isinstance(app, dict):
                            for item2, key2 in app.items():
                                unexpected_info.append(f"\n{item2}: {key2}")
                        else:
                            unexpected_info.append(f"\n-{app}")
                elif isinstance(key, dict):
                    for item2, key2 in key.items():
                        unexpected_info.append(f"\n{item2}: {key2}")
                else:
                    unexpected_info.append(f"{key}")
                answer += f"\n{item} {' '.join(unexpected_info)} "
    return answer


def dynamic_data_filter(data):
    async def func(flt, _, query):
        return bool(re.match(flt.data, query.data))
    return filters.create(func, data=data)


async def get_token(user_id):
    response = await Connections(command="register_user", data={"user_id": user_id}).connection()
    return await(reader(json.loads(response)))


async def connect_to_pc(user_id):
    response = await Connections(command="get_info", data={"user_id": user_id}).connection()
    return json.loads(response), await(reader(json.loads(response), unexpected_info_need=False))

