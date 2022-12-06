make_migrations:
	docker-compose run --rm web sh -c "python manage.py makemigrations $(app)"
migrate:
	docker-compose run --rm web sh -c "python manage.py migrate"
elastic_rebuild:
	docker-compose run --rm web sh -c "python manage.py search_index --rebuild -f"
test:
	docker-compose run --rm web sh -c "python manage.py test $(module)"
super:
	docker-compose run --rm web sh -c "python manage.py createsuperuser"
shell:
	docker-compose run --rm web sh -c "python manage.py shell"
ssh_w:
	docker-compose exec web sh
seed_db:
	docker-compose run --rm web sh -c "python manage.py seed_db"
flush_db:
	docker-compose run --rm web sh -c "python manage.py flush_db"