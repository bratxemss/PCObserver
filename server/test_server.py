async def test_server(client):
    message = {}
    response = await client.send_message(message)
    assert response
    assert not response["success"]
    assert response.get("message") == "Command not found."


async def test_register_app(client):
    message = {
        "command": "register_app",
        "data":
            {
                "user_id": 1235641635,
                "application": {
                    "name": "Doom 2016",
                    "path": "C:/Users/bratx/Desktop/Bread & Fred Demo.url",
                    "size": 202,
                    "status": True,
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
    assert response["message"] == "User login successfully"
    user = await Customer.select().first()
    assert response["information"] == [
        {
            "telegram_id": str(message["data"]["user_id"]),
            "user_token": user.user_token,
            "pc_token": user.pc_token
        }
    ]
    assert len(response["information"])
