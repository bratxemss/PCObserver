async def test_get_token(server_client):
    from .utils import get_token

    server_client.return_value = (
        '{"success": true, "message": "User registered successfully", '
        '"data": {"telegram_id": "12345678", "user_token": "USER_FAKE_TOKEN", "pc_token": "PC_FAKE_TOKEN"}}'
    )

    res = await get_token(1)
    assert res
    assert res == '✅ User registered successfully! ✅\ndata \ntelegram_id: 12345678 \nuser_token: USER_FAKE_TOKEN \npc_token: PC_FAKE_TOKEN '  # noqa
