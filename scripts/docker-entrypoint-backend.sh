#!/bin/sh

set -e

echo "Waiting for DB..."
# wait for Postgres to be ready
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is up!"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Ensuring superuser exists..."
python manage.py createsu

echo "Starting: $@"
exec "$@"























# working code

############ #!/bin/sh ########

# echo "Waiting for DB..."
# # wait for Postgres to be ready
# while ! nc -z db 5432; do
#   sleep 1
# done
# echo "Database is up!"

# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# echo "Starting: $@"
# exec "$@"
