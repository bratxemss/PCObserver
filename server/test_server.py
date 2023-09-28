from .models import Application


async def test_server(client):
    message = {}
    response = await client.send_message(message)
    assert response
    assert not response["success"]
    assert response.get("message") == "User_id is missing."


async def test_register_app(client):
    user_id = 1235641635
    message = {"command": "connect", "data": {"user_id": user_id}}
    await client.send_message(message)

    message = {
        "command": "register_app",
        "data":
            {
                "user_id": user_id,
                "application": {
                    "name": "Doom 2016",
                    "path": "C:/Users/bratx/Desktop/Bread & Fred Demo.url",
                    "size": 202,
                    "status": True,
                    "favorite": False
                }
            }
    }

    response = await client.send_message(message)
    assert response
    assert response["success"]
    assert response["message"]
    assert response["applications"]
    assert len(response["applications"])


async def test_register_user(client):
    from .models import Customer
    assert await Customer.select().count() == 0
    message = {
        "command": "register_user",
        "data":
            {
                "user_id": 1235641635
            }
    }

    response = await client.send_message(message)
    assert await Customer.select().count() == 1
    assert response
    assert response["success"]
    assert response["message"] == "User registered successfully"
    user = await Customer.select().first()
    assert response["data"] == {
        "telegram_id": message["data"]["user_id"],
        "user_token": user.user_token,
        "pc_token": user.pc_token
    }


async def test_get_application_info(client, application):
    user_id = 1235641635
    message = {"command": "connect", "data": {"user_id": user_id}}
    await client.send_message(message)

    message = {
        "command": "get_application_info",
        "data":
            {
                "user_id": user_id,
                "app_id": 1
            }
    }
    response = await client.send_message(message)
    assert response
    assert response["success"]
    assert response["message"] == "Application information found successfully"
    assert (response["information"] ==
            await Application.get_app_by_id(message['data']['user_id'], message['data']['app_id']))


async def test_get_info(client, application):
    user_id = 1235641635
    message = {"command": "connect", "data": {"user_id": user_id}}
    await client.send_message(message)

    message = {
        "command": "get_info",
        "data":
            {
                "user_id": user_id,
            }
    }

    response = await client.send_message(message)
    assert response
    assert response["success"]
    assert response["message"] == "Connected successfully"
    assert response["applications"] == await Application.get_apps_by_user(message['data']['user_id'])

    
async def test_delete_app(client, application):
    from .models import Application

    user_id = 1235641635
    message = {"command": "connect", "data": {"user_id": user_id}}
    await client.send_message(message)

    assert await Application.select().count() == 1
    message = {
        "command": "delete_app",
        "data":
            {
                "user_id": user_id,
                "application": {
                    "id": 1
                }
            }
    }
    response = await client.send_message(message)
    assert await Application.select().count() == 0
    assert response
    assert response["success"]
    assert response["message"] == "Deleted successfully"
    assert response["app_id"] == message["data"]["application"]["id"]

# make this test get response from command "turn"
#
# async def test_turn_on(client, application):
#     user_id = 1235641635
#     message = {"command": "connect", "data": {"user_id": user_id}}
#     await client.send_message(message)
#
#     message = {"command": "turn", "data": {"user_id": user_id, "app_id": 1, "command": "On"}}
#     response = await client.send_message(message)
#     assert response
