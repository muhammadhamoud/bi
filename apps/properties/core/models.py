from django.db import models
from django.utils.text import slugify

from apps.core.common.models import ActivatableModel, NamedSlugModel, TimeStampedModel


class Organization(NamedSlugModel):
    class BusinessType(models.TextChoices):
        HOTEL_GROUP = 'hotel_group', 'Hotel Group'
        RESTAURANT_GROUP = 'restaurant_group', 'Restaurant Group'
        HOSPITALITY = 'hospitality', 'Hospitality'
        MERCHANT = 'merchant', 'Merchant'

    code = models.CharField(max_length=40, unique=True)
    business_type = models.CharField(max_length=40, choices=BusinessType.choices, default=BusinessType.HOSPITALITY)
    headquarters_city = models.CharField(max_length=80, blank=True)
    headquarters_country = models.CharField(max_length=80, blank=True)

    class Meta:
        db_table = 'organizations'
        ordering = ['name']


class Property(TimeStampedModel, ActivatableModel):
    class PropertyType(models.TextChoices):
        HOTEL = 'hotel', 'Hotel'
        RESTAURANT = 'restaurant', 'Restaurant'
        RESORT = 'resort', 'Resort'
        APARTMENT = 'apartment', 'Apartment'
        CLUSTER = 'cluster', 'Cluster'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='properties')
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    code = models.CharField(max_length=40, unique=True)
    resort = models.CharField(max_length=40, unique=True)
    property_type = models.CharField(max_length=40, choices=PropertyType.choices, default=PropertyType.HOTEL)
    city = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=80, blank=True)
    currency = models.CharField(max_length=10, default='AED')
    timezone = models.CharField(max_length=80, default='Asia/Dubai')
    total_rooms = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'properties'
        ordering = ['organization__name', 'name']
        permissions = [
            ('view_dashboard', 'Can view business dashboards'),
            ('view_reports', 'Can view embedded reports'),
            ('view_dataops', 'Can view data operations'),
            ('manage_mappings', 'Can manage mapping settings'),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.organization.code}-{self.name}')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# from apps.settings.mappings.services.segment_defaults import seed_default_segments_for_property

# property_obj = form.save()
# seed_default_segments_for_property(property_obj=property_obj, actor=request.user)