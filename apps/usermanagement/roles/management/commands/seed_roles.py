from django.core.management.base import BaseCommand

from apps.usermanagement.roles.services import seed_default_groups


class Command(BaseCommand):
    help = 'Seed default role groups and baseline permissions.'

    def handle(self, *args, **options):
        seed_default_groups()
        self.stdout.write(self.style.SUCCESS('Role groups seeded.'))
