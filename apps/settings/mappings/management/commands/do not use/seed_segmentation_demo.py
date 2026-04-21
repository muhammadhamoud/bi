from django.core.management.base import BaseCommand

from apps.dataops.files.models import SourceSystem
from apps.properties.core.models import Property
from apps.settings.mappings.models import Segment, SegmentCategory, SegmentDetail, SegmentGroup


class Command(BaseCommand):
    help = 'Seed demo market segmentation hierarchy and mappings.'

    def handle(self, *args, **options):
        property_obj = Property.objects.filter(is_active=True).first()
        if not property_obj:
            self.stdout.write(self.style.WARNING('No properties found. Run seed_properties first.'))
            return
        source_system = SourceSystem.objects.filter(is_active=True).first()
        group, _ = SegmentGroup.objects.get_or_create(property=property_obj, code='LEISURE', defaults={'name': 'Leisure', 'description': 'Leisure travel segment'})
        category, _ = SegmentCategory.objects.get_or_create(property=property_obj, group=group, code='OTA', defaults={'name': 'Online travel agencies'})
        segment, _ = Segment.objects.get_or_create(property=property_obj, group=group, category=category, code='OTA-TRANSIENT', defaults={'name': 'OTA transient'})
        SegmentDetail.objects.get_or_create(
            property=property_obj,
            segment=segment,
            source_code='BKEXP',
            defaults={
                'source_system': source_system,
                'source_label': 'Booking.com Expected',
                'mapped_code': 'OTA-TRANS',
                'mapped_label': 'OTA Transient',
                'notes': 'Mapped from PMS market segment',
            },
        )
        SegmentDetail.objects.get_or_create(
            property=property_obj,
            segment=segment,
            source_code='UNMAPPED-OTA',
            defaults={
                'source_system': source_system,
                'source_label': 'Unknown OTA Segment',
                'mapped_code': '',
                'mapped_label': '',
                'is_review_required': True,
                'notes': 'Requires manual classification',
            },
        )
        self.stdout.write(self.style.SUCCESS('Segmentation demo data seeded.'))
