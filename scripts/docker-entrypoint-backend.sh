#!/bin/sh

echo "Waiting for DB..."
# wait for Postgres to be ready
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is up!"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting: $@"
exec "$@"