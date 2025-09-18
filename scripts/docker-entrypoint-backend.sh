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

echo "Creating superuser if not exists..."
python manage.py createsu

echo "Starting: $@"
exec "$@"






























# #!/bin/sh

# set -e

# echo "Waiting for DB..."
# # wait for Postgres to be ready
# while ! nc -z db 5432; do
#   sleep 1
# done
# echo "Database is up!"

# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# echo "Running migrations..."
# python manage.py makemigrations --noinput
# python manage.py migrate --noinput

# echo "Creating superuser if not exists..."
# python manage.py shell -c "
# from django.contrib.auth import get_user_model
# import os
# User = get_user_model()
# email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
# if not User.objects.filter(email=email).exists():
#     User.objects.create_superuser(
#         email=email,
#         password=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin'),
#         first_name=os.environ.get('DJANGO_SUPERUSER_FIRST_NAME', 'Admin'),
#         last_name=os.environ.get('DJANGO_SUPERUSER_LAST_NAME', 'Smith')
#     )
#     print(f'Superuser {email} created successfully!')
# else:
#     print(f'Superuser {email} already exists.')
# "

# echo "Starting: $@"
# exec "$@"

