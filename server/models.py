import peewee as pw
from peewee_aio.model import AIOModel

from . import db


@db.register
class Customer(AIOModel):
    telegram_id = pw.CharField(unique=True)
    user_token = pw.CharField(null=True)
    pc_token = pw.CharField(null=True)
    pc_status = pw.CharField(null=True)

    def __repr__(self):
        return f"<Customer: {self.telegram_id}>"


@db.register
class Application(AIOModel):
    user = pw.ForeignKeyField(Customer, to_field=Customer.telegram_id)
    app_path = pw.CharField(null=True)
    app_name = pw.CharField(null=True)
    app_size = pw.IntegerField(default=0)
    app_status = pw.BooleanField(default=False)

    def __repr__(self):
        return f"<Application: {self.user}, {self.app_name}, {self.app_path}, {self.app_size}, {self.app_status}>"
