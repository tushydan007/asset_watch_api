from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = "Create a superuser if none exists"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "admin123")

        if not User.objects.filter(username=username).exists():
            self.stdout.write("Creating superuser...")
            User.objects.create_superuser(
                username=username, email=email, password=password, first_name=first_name,
                last_name=last_name,
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser {username} created."))
        else:
            self.stdout.write(
                self.style.WARNING(f"Superuser {username} already exists. Skipping.")
            )
