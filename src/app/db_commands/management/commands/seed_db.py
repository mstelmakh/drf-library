from db_commands.services import seed_db

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Django CLI command used to seed database from local JSON file.
    Args:
        f: Path to json file (optional).
    """
    help = "Seed database from local JSON file."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--f', type=str, help="Path to directory with json files. (default: resources)"
        )

    def handle(self, *args, **options):
        path = None
        self.stdout.write('Seeding database...')
        seed_db(path) if path else seed_db()
        self.stdout.write(self.style.SUCCESS('Done'))