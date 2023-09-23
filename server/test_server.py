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


async def test_add_to_favorite(client, application):
    user_id = 1235641635
    application_id = 1

    connect_message = {"command": "connect", "data": {"user_id": user_id}}
    await client.send_message(connect_message)

    initial_application = await Application.get_app_by_id(user_id, application_id)
    assert initial_application[0].get("favorite") is False

    response = await client.send_message({
        "command": "add_to_favorite",
        "data": {"user_id": user_id, "application": {"id": application_id}}
    })

    updated_application = await Application.get_app_by_id(user_id, application_id)
    assert updated_application[0].get("favorite") is True

    assert response
    assert response["success"]
    assert response["message"] == "Application successfully added to favorite"


async def test_remove_from_favorite(client):
    await Application.create(
        user=1235641635,
        app_name="app_name",
        app_path="app_path",
        app_size="app_size",
        app_status=False,
        app_favorite=True
    )
    user_id = 1235641635
    application_id = 1

    connect_message = {"command": "connect", "data": {"user_id": user_id}}
    await client.send_message(connect_message)

    initial_application = await Application.get_app_by_id(user_id, application_id)
    assert initial_application[0].get("favorite") is True

    response = await client.send_message({
        "command": "remove_from_favorite",
        "data": {"user_id": user_id, "application": {"id": application_id}}
    })

    updated_application = await Application.get_app_by_id(user_id, application_id)
    assert updated_application[0].get("favorite") is False

    assert response
    assert response["success"]
    assert response["message"] == "Application successfully removed from favorite"