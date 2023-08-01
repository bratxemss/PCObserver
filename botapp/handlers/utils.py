from uuid import uuid4

from botapp.models import Customer


async def get_token(user_id):
    customer = await Customer.select().where(Customer.telegram_id == user_id).first()
    if not customer:
        customer = await Customer.create(
            telegram_id=user_id,
            user_token=str(uuid4())
        )
    return f"That is your user token --> {customer.user_token}"


async def connect_pc_data(user_id):
    pass


async def connect_to_pc(user_id):
    customer = await Customer.select().where(Customer.telegram_id == user_id).first()
    message = ""
    if not customer:
        message = f"We did not find you token, if you dont have a token, please create one"
    elif customer:
        if not customer.pc_token:
            message = f"We did not find you PC, make shore that you PC application is enabled and configured properly."
        else:
            if customer.pc_status == "Online":
                message = "Connecting..."
                await connect_pc_data(user_id)
            elif customer.pc_status == "Offline":
                message = "Your application is offline"
            else:
                message = "⚠️Is Error appeared while connecting to you data, please message the Customer Service --> ⚠️"
    return message


