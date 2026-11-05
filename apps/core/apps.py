from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Shared vocabulary (hobbies, categories) and the content scope rules."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        # Registers the database-scoped content scope system check.
        from apps.core import checks  # noqa: F401
