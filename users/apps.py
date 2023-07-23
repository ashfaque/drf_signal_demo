from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"

    # ! Signal (2/3) - Add this method
    def ready(self):
        import users.signals      # Replace 'app_name' with the actual name of your app
