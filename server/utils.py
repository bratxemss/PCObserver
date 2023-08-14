from server.models import Application


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
