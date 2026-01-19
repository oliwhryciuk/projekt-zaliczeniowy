from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Generate authentication tokens for all users'

    def handle(self, *args, **options):
        for user in User.objects.all():
            token, created = Token.objects.get_or_create(user=user)
            status = 'created' if created else 'already exists'
            self.stdout.write(
                self.style.SUCCESS(
                    f'Token for {user.username}: {token.key} ({status})'
                )
            )
