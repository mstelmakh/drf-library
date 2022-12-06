from django.core.management.base import BaseCommand

from library.models import Genre, Language, Author, Book, BookInstance


class Command(BaseCommand):
    """
    Django CLI command used to flush database.
    """
    help = "Flush database."

    def handle(self, *args, **options):
        self.stdout.write('Flushing database...')
        for model in (Genre, Language, Author, Book, BookInstance):
            model.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Done'))