async def test_get_token(server_client):
    from .utils import get_token
    server_client.return_value = (
        '{"success": true, "message": "User registered successfully", '
        '"data": {"telegram_id": "12345678", "user_token": "USER_FAKE_TOKEN", "pc_token": "PC_FAKE_TOKEN"}}'
    )
    res = await get_token(1)
    assert res
    print(res)
    assert res == '✅User registered successfully✅\ndata \ntelegram_id: 12345678 \nuser_token: USER_FAKE_TOKEN \npc_token: PC_FAKE_TOKEN '  # noqa


async def test_connect_to_pc(server_client, tg_user):
    from .utils import connect_to_pc
    print(server_client.return_value)
    server_client.return_value = (
        '{"success": false, "message": "Application list is empty", "applications": []}')
    res = await connect_to_pc(1)
    assert res == ('❌Application list is empty❌', {'applications': [], 'message': 'Application list is empty', 'success': False})

    # assert res == '✅User registered successfully✅\ndata \ntelegram_id: 12345678 \nuser_token: USER_FAKE_TOKEN \npc_token: PC_FAKE_TOKEN '  # noqa
