from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


USER: str = "admin"
EMAIL: str = "test@test.com"
PASSWORD: str = "adminadmin"


class Command(BaseCommand):
    help: str = "Create super user without an input"

    def add_arguments(self, parser):
        parser.add_argument("-username", type=str)
        parser.add_argument("-password", type=str)
        parser.add_argument("-email", type=str)

    def handle(self, *args, **options):
        username: str = options.get("username") if options.get("username") else USER
        password: str = options.get("password") if options.get("password") else PASSWORD
        email: str = options.get("email") if options.get("email") else EMAIL

        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write("A super user already exists in the system.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write("=====================================")
        self.stdout.write("Super user created.")
        self.stdout.write("=====================================")
