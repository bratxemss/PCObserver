import re
import json

from .. import bot
from pyrogram import filters


def dynamic_data_filter(data):
    async def func(flt, _, query):
        return bool(re.match(flt.data, query.data))

    return filters.create(func, data=data)


async def reader(message: dict, need_of_unexpected_info=True) -> str:
    unexpected_info = []
    answer = ""
    if message.get("message"):
        answer += f"{message['message']}"
    if message.get("success"):
        answer = "✅" + answer + "✅"
    elif not message.get("success"):
        answer = "❌" + answer + "❌"
    if need_of_unexpected_info:
        for item, key in message.items():
            if item != "message" and item != "success":
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


async def get_token(user_id):
    response = await bot.servers_client.send_message(command="register_user", data={"user_id": user_id})
    return await(reader(json.loads(response)))


async def connect_to_pc(user_id):
    response = await bot.servers_client.send_message(command="get_info", data={"user_id": user_id})
    return await(reader(json.loads(response), need_of_unexpected_info=False)), json.loads(response)


async def get_application_data(user_id, app_id):
    response = await bot.servers_client.send_message(command="get_application_info", data={
        "user_id": user_id,
        "app_id": app_id,
    })
    return await(reader(json.loads(response)))


async def send_request_to_customer(user_id, app_id, command: str):
    if app_id:
        response = await bot.servers_client.send_message(command="send_command", data={
            "command": command,
            "user_id": user_id,
            "data": {
                "app_id": app_id,
            }
        })
    else:
        response = await bot.servers_client.send_message(command="send_command", data={
            "command": command,
            "user_id": user_id,
        })
    return await(reader(json.loads(response)))
