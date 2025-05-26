#!/bin/sh

# Entrypoint script to set up and run the Django application

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8000 foodgram.wsgi:application