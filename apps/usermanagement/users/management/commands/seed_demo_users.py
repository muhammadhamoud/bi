from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from apps.properties.core.models import Property
from apps.usermanagement.roles.services import ROLE_ADMIN, ROLE_MANAGER, ROLE_MERCHANT_OWNER, ROLE_OPERATOR, ROLE_VIEWER
from apps.usermanagement.users.services import sync_user_properties, sync_user_role

User = get_user_model()
DEMO_PASSWORD = 'DemoPass123!'


class Command(BaseCommand):
    help = 'Seed demo users for every role.'

    def handle(self, *args, **options):
        properties = list(Property.objects.all())
        if not properties:
            self.stdout.write(self.style.WARNING('No properties found. Run seed_properties first.'))
            return

        users = [
            # {'email': 'admin@horizonbi.local', 'username': 'admin', 'first_name': 'Amina', 'last_name': 'Admin', 'role': ROLE_ADMIN, 'properties': properties},
            {'email': 'manager@horizonbi.local', 'username': 'manager', 'first_name': 'Mason', 'last_name': 'Manager', 'role': ROLE_MANAGER, 'properties': properties[:2]},
            {'email': 'operator@horizonbi.local', 'username': 'operator', 'first_name': 'Olivia', 'last_name': 'Operator', 'role': ROLE_OPERATOR, 'properties': properties[:1]},
            {'email': 'merchant@horizonbi.local', 'username': 'merchant', 'first_name': 'Maya', 'last_name': 'Merchant', 'role': ROLE_MERCHANT_OWNER, 'properties': properties[:2]},
            {'email': 'viewer@horizonbi.local', 'username': 'viewer', 'first_name': 'Victor', 'last_name': 'Viewer', 'role': ROLE_VIEWER, 'properties': properties[:1]},
        ]

        for data in users:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'username': data['username'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'is_active': True,
                },
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
            sync_user_role(user, data['role'])
            sync_user_properties(user, data['properties'])

        self.stdout.write(self.style.SUCCESS('Demo users seeded. Password for all demo users: DemoPass123!'))
