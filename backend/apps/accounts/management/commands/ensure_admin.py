import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Idempotently ensures a superuser account exists.

    Runs on every container start (see docker-entrypoint.sh) so a fresh
    `docker compose up --build` always has an admin login, without ever
    failing on a second run the way `createsuperuser --noinput` does.
    Reads DJANGO_SUPERUSER_EMAIL/USERNAME/PASSWORD, falling back to the
    project's one seeded account if unset.
    """

    help = "Create or update the seeded admin/superuser account from environment variables."

    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "devmitori@gmail.com")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "Admin@Movies2026")
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "devmitori")

        User = get_user_model()
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": username},
        )
        user.username = username
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()

        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} admin account for {email}"))
