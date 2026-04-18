from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed a complete demo environment across all major modules.'

    def handle(self, *args, **options):
        for command_name in [
            'seed_roles',
            'seed_properties',
            'seed_demo_users',
            'seed_analytics_demo',
            'seed_notifications_demo',
            'seed_powerbi_demo',
            'seed_dataops_demo',
            'seed_mapping_demo',
            'seed_segmentation_demo',
        ]:
            self.stdout.write(self.style.NOTICE(f'Running {command_name}...'))
            call_command(command_name)
        self.stdout.write(self.style.SUCCESS('All demo data seeded successfully.'))
