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
