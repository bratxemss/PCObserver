from server.models import Application


async def get_user_app(user_id, app_id):
    user_application = await Application.select().where(
        Application.user == user_id,
        Application.id == app_id
    ).first()
    if user_application:
        app_info = [{
            "name": user_application.app_name,
            "path": user_application.app_path,
            "size": user_application.app_size,
            "status": user_application.app_status
        }]
        return app_info


async def get_users_apps(user_id):
    user_applications = await Application.select().where(
        Application.user == user_id
    )
    return [
        {
            "id": app.id,
            "name": app.app_name,
            "path": app.app_path,
            "size": app.app_size,
            "status": app.app_status
        }
        for app in user_applications
    ]
