from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.common.models import ActivatableModel, TimeStampedModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The email address is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if not extra_fields.get('username'):
            extra_fields['username'] = email.split('@')[0]
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=40, blank=True)
    job_title = models.CharField(max_length=120, blank=True)
    display_name = models.CharField(max_length=150, blank=True)
    preferences = models.JSONField(default=dict, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    class Meta:
        db_table = 'users'
        ordering = ['email']

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.strip().lower()
        if self.username:
            self.username = self.username.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name() or self.email

    @property
    def primary_role(self):
        from apps.usermanagement.roles.services import get_highest_role

        return get_highest_role(self)

    @property
    def name_or_email(self):
        return self.display_name or self.get_full_name() or self.email


class UserPropertyAccess(TimeStampedModel, ActivatableModel):
    user = models.ForeignKey('usercore.User', on_delete=models.CASCADE, related_name='property_assignments')
    property = models.ForeignKey('propertycore.Property', on_delete=models.CASCADE, related_name='assignments')
    is_primary = models.BooleanField(default=False)
    assigned_by = models.ForeignKey('usercore.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_properties')
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'user_property_access'
        unique_together = ('user', 'property')
        ordering = ['user__email', 'property__name']

    def __str__(self):
        return f'{self.user.email} -> {self.property.name}'
