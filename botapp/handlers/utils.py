from .. import bot
import json


async def reader(message: dict) -> str:
    unexpected_info = []
    answer = ""
    if message.get("message"):
        answer += f"{message['message']}! "
    if message.get("status"):
        if message.get("status") == "success":
            answer = "✅ " + answer + "✅"
        elif message.get("status") == "error":
            answer = "❌ " + answer + "❌"
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


async def get_token(user_id):
    response = await bot.servers_client.send_message(command="register_user", data={"user_id": user_id})
    return await(reader(json.loads(response)))


async def connect_to_pc(user_id):
    response = await bot.servers_client.send_message(command="get_info", data={"user_id": user_id})
    return await(reader(json.loads(response)))

