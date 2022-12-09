from django.apps import AppConfig


class LibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'library'

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signals
        # Explicitly connect a signal handler.