from django.core.management import call_command

from django.core.management.base import BaseCommand
from django.db import transaction


FIXTURES = (
    "db_genre_fixture.json",
    "db_language_fixture.json",
    "db_author_fixture.json",
    "db_book_fixture.json",
    "db_book_instance_fixture.json",
)


class Command(BaseCommand):
    help = "Seed database from fixtures."

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')
        call_command("makemigrations")
        call_command("migrate")

        with transaction.atomic():
            for fixture in FIXTURES:
                call_command("loaddata", fixture)
        self.stdout.write(self.style.SUCCESS('Done'))