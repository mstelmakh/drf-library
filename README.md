# Library Management System

Project helps to manage the library. Allows users to view and reserve books and helps librarian to keep track of books.

## General
- Two roles: user and librarian
- User can make/cancel book reservation
- Librarian can mark the book as borrowed or as returned
- If the book is reserved/borrowed by other user, user can enable notifications on this book status
- Searching genres, languages, authors, books and book instances

## Technologies used
- Docker
- Django Rest Framework
- PostgreSQL
- JWT
- Elasticsearch
- Celery & Redis

## Start
1. Override `.env.example` file or create new (in this case you would also need to change environment file in `docker-compose.yml`).

2. `docker-compose up`

## Seed database with test data
You can seed database with test data defined in json files in `src/library/app/fixtures` folder using django-admin command:
```sh
# Seed database
python manage.py seed_db

# Flush database
python manage.py flush_db
```
Or in Docker
```sh
# Seed database
make seed_db

# Flush database
make flush_db
```

## Testing
For testing use:

`python3 manage.py test`

For Docker:

`make test`