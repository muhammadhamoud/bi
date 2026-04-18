from django.conf import settings
from django.db import models

from apps.core.common.models import TimeStampedModel


class Profile(TimeStampedModel):
    class ThemePreference(models.TextChoices):
        SYSTEM = 'system', 'System'
        LIGHT = 'light', 'Light'
        DARK = 'dark', 'Dark'

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    timezone = models.CharField(max_length=80, default='Asia/Dubai')
    theme_preference = models.CharField(max_length=20, choices=ThemePreference.choices, default=ThemePreference.SYSTEM)
    locale = models.CharField(max_length=20, default='en')
    bio = models.TextField(blank=True)
    receive_email_notifications = models.BooleanField(default=True)
    receive_product_announcements = models.BooleanField(default=True)

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return f'Profile<{self.user.email}>'
