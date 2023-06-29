import peewee as pw
from peewee_aio.model import AIOModel

from botapp import bot


@bot.db.register
class Customer(AIOModel):
    telegram_id = pw.CharField(unique=True)
    user_token = pw.CharField(null=True)
    pc_token = pw.CharField(null=True)
    pc_status = pw.CharField(null=True)

    def __repr__(self):
        return f"<Customer: {self.phone}>"