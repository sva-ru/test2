#!/bin/sh

sleep 10

celery -A netology_pd_diplom worker -D
python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate

gunicorn netology_pd_diplom.wsgi:application -b 0.0.0.0:8000

exec "$@"