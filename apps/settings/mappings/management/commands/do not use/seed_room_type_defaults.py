# apps/settings/mappings/management/commands/seed_room_type_defaults.py

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.properties.core.models import Property
from apps.settings.mappings.data_dontuse.room_type_defaults import seed_default_room_types_for_property

# python manage.py seed_room_type_defaults --property-code P6
# python manage.py seed_room_type_defaults --property-id 1000
# python manage.py seed_room_type_defaults --all

class Command(BaseCommand):
    help = 'Seed predefined room type groups, categories, and mappings for one or more properties.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--property-id',
            type=int,
            nargs='*',
            help='One or more property IDs to seed.',
        )
        parser.add_argument(
            '--property-code',
            type=str,
            nargs='*',
            help='One or more property codes to seed.',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Seed all properties.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        property_ids = options.get('property_id') or []
        property_codes = options.get('property_code') or []
        seed_all = options.get('all', False)

        queryset = Property.objects.all()

        if seed_all:
            properties = queryset
        elif property_ids:
            properties = queryset.filter(id__in=property_ids)
        elif property_codes:
            properties = queryset.filter(code__in=property_codes)
        else:
            raise CommandError('Provide --all, --property-id, or --property-code.')

        if not properties.exists():
            raise CommandError('No matching properties found.')

        for property_obj in properties.order_by('id'):
            seed_default_room_types_for_property(property_obj, actor=None)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Seeded room type defaults for property {property_obj.code} - {property_obj.name}'
                )
            )