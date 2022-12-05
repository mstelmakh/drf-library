import os
import sys
import json

from django.conf import settings
from django.db import transaction

from library.models import Genre, Language, Author, Book, BookInstance


DEFAULT_JSON_DIR = "resources"

LANGUAGES_JSON = "languages.json"
GENRES_JSON = "genres.json"
AUTHORS_JSON = "authors.json"
BOOKS_JSON = "books.json"
BOOK_INSTANCES_JSON = "book_instances.json"


def path_to(dir, file):
    return os.path.join(
        settings.BASE_DIR.parent, dir, file
    )


def read_from_json(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data


def import_from_json(model, path, related_fields=None):
    objects = read_from_json(path)

    for object in objects:
        object_sets = []

        if related_fields:
            for field in related_fields:
                if isinstance(object[field[0]], list):
                    object_sets.append((field[0], [field[1].objects.get(pk=id) for id in object[field[0]]]))
                    del object[field[0]]
                else:
                    object[field[0]] = field[1].objects.get(pk=object[field[0]])

        created_object = model.objects.create(**object)

        for object_set in object_sets:
            getattr(created_object, object_set[0]).add(*object_set[1])


def seed_db(json_dir=DEFAULT_JSON_DIR):
    with transaction.atomic():
        import_from_json(Language, path_to(json_dir, LANGUAGES_JSON))
        import_from_json(Genre, path_to(json_dir, GENRES_JSON))
        import_from_json(Author, path_to(json_dir, AUTHORS_JSON))
        import_from_json(
            Book, 
            path_to(json_dir, BOOKS_JSON),
            (
                ("language", Language),
                ("genre", Genre),
                ("author", Author)
            )
        )
        import_from_json(
            BookInstance,
            path_to(json_dir, BOOK_INSTANCES_JSON),
            (("book", Book), )
        )


def flush_db():
    for model in (Language, Genre, Author, Book, BookInstance):
        model.objects.all().delete()