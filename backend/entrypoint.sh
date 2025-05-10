#!/bin/sh

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Running makemigrations..."
python manage.py makemigrations

echo "Running migrate..."
python manage.py migrate

echo "Importing ingredients..."
python manage.py import_ingredients

echo "Starting Gunicorn..."
exec gunicorn foodgram_backend.wsgi:application --bind 0.0.0.0:8000
