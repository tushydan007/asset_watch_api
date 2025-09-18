#!/bin/bash

# Create migrations
python manage.py makemigrations accounts
python manage.py makemigrations aoi
python manage.py makemigrations orders
python manage.py makemigrations payments
python manage.py makemigrations notifications
python manage.py makemigrations monitoring

# Run migrations
python manage.py migrate

# Create superuser (interactive)
echo "Creating superuser..."
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

echo "Setup complete!"