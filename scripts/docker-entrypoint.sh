#!/bin/sh

echo "Waiting for DB..."
# wait for Postgres to be ready
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is up!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Django..."
exec "$@"






# celery-beat:
#   command: >
#     sh -c "python manage.py migrate &&
#            celery -A asset_watch beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler"
#     depends_on:
#       - django_backend
#     container_name: celery_beat
#     image: django_backend
#     volumes:
#       - .:/app
#       - static_volume:/app/staticfiles
#       - media_volume:/app/media
#     env_file:           
#       - .env
#     restart: always
#     networks:
#       - asset_watch_network             