make_migrations:
	docker-compose run --rm web sh -c "python manage.py makemigrations bank"
migrate:
	docker-compose run --rm web sh -c "python manage.py migrate"
test:
	docker-compose run --rm web sh -c "python manage.py test"
super:
	docker-compose run --rm web sh -c "python manage.py createsuperuser"
shell:
	docker-compose run --rm web sh -c "python manage.py shell"
ssh_w:
	docker-compose exec web sh