from django.core.management.base import BaseCommand

from apps.properties.core.models import Organization, Property


class Command(BaseCommand):
    help = 'Seed demo organizations and properties.'

    def handle(self, *args, **options):
        org, _ = Organization.objects.get_or_create(
            code='SHG',
            defaults={
                'name': 'Seaside Hospitality Group',
                'business_type': Organization.BusinessType.HOTEL_GROUP,
                'headquarters_city': 'Dubai',
                'headquarters_country': 'UAE',
            },
        )
        org2, _ = Organization.objects.get_or_create(
            code='URB',
            defaults={
                'name': 'Urban Plate Collective',
                'business_type': Organization.BusinessType.RESTAURANT_GROUP,
                'headquarters_city': 'Abu Dhabi',
                'headquarters_country': 'UAE',
            },
        )
        defaults = [
            {'organization': org, 'code': 'DXB-MARINA', 'name': 'Marina Bay Hotel', 'property_type': Property.PropertyType.HOTEL, 'city': 'Dubai', 'country': 'UAE', 'currency': 'AED', 'total_rooms': 220},
            {'organization': org, 'code': 'AUH-CORN', 'name': 'Corniche Suites', 'property_type': Property.PropertyType.RESORT, 'city': 'Abu Dhabi', 'country': 'UAE', 'currency': 'AED', 'total_rooms': 180},
            {'organization': org2, 'code': 'DXB-DOWNT', 'name': 'Downtown Bistro', 'property_type': Property.PropertyType.RESTAURANT, 'city': 'Dubai', 'country': 'UAE', 'currency': 'AED', 'total_rooms': 0},
        ]
        for item in defaults:
            Property.objects.get_or_create(code=item['code'], defaults=item)
        self.stdout.write(self.style.SUCCESS('Properties seeded.'))
