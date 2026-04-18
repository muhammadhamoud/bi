from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.notifications.announcements.models import Announcement
from apps.notifications.inbox.models import Notification
from apps.properties.core.models import Property

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo notifications and announcements.'

    def handle(self, *args, **options):
        properties = list(Property.objects.all())
        for user in User.objects.all():
            Notification.objects.get_or_create(
                recipient=user,
                title='Daily metrics refreshed',
                defaults={
                    'message': 'The overnight metrics refresh completed successfully for your assigned properties.',
                    'level': Notification.Level.SUCCESS,
                    'link_url': '/analytics/executive/',
                },
            )
            Notification.objects.get_or_create(
                recipient=user,
                title='Action needed on missing files',
                defaults={
                    'message': 'A missing daily pickup file requires review in DataOps.',
                    'level': Notification.Level.WARNING,
                    'link_url': '/dataops/missing-files/',
                },
            )
        announcement, _ = Announcement.objects.get_or_create(
            title='Monthly executive review pack published',
            defaults={
                'body': 'The month-end executive review pack is now available in the embedded reports section.',
                'level': Announcement.Level.INFO,
                'is_published': True,
                'starts_at': timezone.now(),
            },
        )
        if properties:
            announcement.properties.set(properties[:2])
        self.stdout.write(self.style.SUCCESS('Notifications and announcements seeded.'))
