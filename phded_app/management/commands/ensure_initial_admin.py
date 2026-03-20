import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from phded_app.models import UserProfile


class Command(BaseCommand):
    help = "Create or update the initial admin account for deployments."

    def handle(self, *args, **options):
        email = os.environ.get("INITIAL_ADMIN_EMAIL", "admin@phded.com").strip().lower()
        password = os.environ.get("INITIAL_ADMIN_PASSWORD", "Admin@123")
        first_name = os.environ.get("INITIAL_ADMIN_FIRST_NAME", "Admin").strip()
        last_name = os.environ.get("INITIAL_ADMIN_LAST_NAME", "").strip()

        user, created = User.objects.get_or_create(
            email__iexact=email,
            defaults={
                "username": email,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
            },
        )

        updated_fields = []
        if user.username != email:
            user.username = email
            updated_fields.append("username")
        if user.email != email:
            user.email = email
            updated_fields.append("email")
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updated_fields.append("first_name")
        if user.last_name != last_name:
            user.last_name = last_name
            updated_fields.append("last_name")
        if not user.is_staff:
            user.is_staff = True
            updated_fields.append("is_staff")
        if not user.is_superuser:
            user.is_superuser = True
            updated_fields.append("is_superuser")

        user.set_password(password)
        updated_fields.append("password")
        user.save(update_fields=updated_fields)

        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={"role": "admin"},
        )
        if profile.role != "admin":
            profile.role = "admin"
            profile.save(update_fields=["role"])

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created initial admin user {email}."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Updated initial admin user {email}."))

        if profile_created:
            self.stdout.write(self.style.SUCCESS("Created admin user profile."))
