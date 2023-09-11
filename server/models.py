from uuid import uuid4

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

    @classmethod
    async def create_with_telegram_id(cls, telegram_id):
        return await cls.create(
            telegram_id=telegram_id,
            user_token=str(uuid4()),
            pc_token=str(uuid4())
        )


@db.register
class Application(AIOModel):
    user = pw.ForeignKeyField(Customer, to_field=Customer.telegram_id)
    app_path = pw.CharField(null=True)
    app_name = pw.CharField(null=True)
    app_size = pw.IntegerField(default=0)
    app_status = pw.BooleanField(default=False)
    app_favorite = pw.BooleanField(default=False)

    def __repr__(self):
        return f"<Application: {self.id}, {self.user}, {self.app_name}>"

    @classmethod
    async def get_app_by_id(cls, user_id, app_id):
        user_application = await cls.select().where(
            cls.user == user_id,
            cls.id == app_id
        ).first()
        if user_application:
            app_info = [{
                "name": user_application.app_name,
                "path": user_application.app_path,
                "size": user_application.app_size,
                "status": user_application.app_status,
                "favorite": user_application.app_favorite
            }]
            return app_info

    @classmethod
    async def get_apps_by_user(cls, user_id):
        user_applications = await cls.select().where(
            cls.user == user_id
        )
        return [
            {
                "id": app.id,
                "name": app.app_name,
                "path": app.app_path,
                "size": app.app_size,
                "status": app.app_status,
                "favorite": app.app_favorite
            }
            for app in user_applications
        ]
