from db_commands.services import flush_db

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Django CLI command used to flush database.
    """
    help = "Flush database."

    def handle(self, *args, **options):
        self.stdout.write('Flushing database...')
        flush_db()
        self.stdout.write(self.style.SUCCESS('Done'))