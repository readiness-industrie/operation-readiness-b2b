import getpass

from django.contrib.auth.password_validation import validate_password
from django.core.management.base import BaseCommand, CommandError

from operations.db import rls_context
from operations.enums import UserRole
from operations.models import User


class Command(BaseCommand):
    help = "Crée le compte Owner nominatif initial."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--email", required=True)

    def handle(self, *args, **options):
        password = getpass.getpass("Mot de passe (14 caractères minimum) : ")
        validate_password(password)
        with rls_context(owner=True):
            if User.objects.filter(role=UserRole.OWNER).exists():
                raise CommandError("Un compte Owner existe déjà. Aucun compte partagé supplémentaire n'a été créé.")
            user = User(username=options["username"], email=options["email"], role=UserRole.OWNER, is_staff=False, is_superuser=False)
            user.set_password(password)
            user.full_clean()
            user.save()
        self.stdout.write(self.style.SUCCESS("Owner créé. Le MFA sera configuré à la première connexion."))
