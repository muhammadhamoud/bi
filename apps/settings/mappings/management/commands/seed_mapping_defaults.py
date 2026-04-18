# apps/settings/mappings/management/commands/seed_mapping_defaults.py

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.properties.core.models import Property
from apps.settings.mappings.data.room_type_defaults import seed_default_room_types_for_property
from apps.settings.mappings.data.segment_defaults import seed_default_segments_for_property


# python manage.py seed_mapping_defaults --property-code P6 --room-types-only
# python manage.py seed_mapping_defaults --all


class Command(BaseCommand):
    help = 'Seed default mapping structures for one or more properties.'

    def add_arguments(self, parser):
        parser.add_argument('--property-id', type=int, nargs='*')
        parser.add_argument('--property-code', type=str, nargs='*')
        parser.add_argument('--all', action='store_true')
        parser.add_argument('--segments-only', action='store_true')
        parser.add_argument('--room-types-only', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        property_ids = options.get('property_id') or []
        property_codes = options.get('property_code') or []
        seed_all = options.get('all', False)
        segments_only = options.get('segments_only', False)
        room_types_only = options.get('room_types_only', False)

        if segments_only and room_types_only:
            raise CommandError('Use only one of --segments-only or --room-types-only.')

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
            if not room_types_only:
                seed_default_segments_for_property(property_obj, actor=None)

            if not segments_only:
                seed_default_room_types_for_property(property_obj, actor=None)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Seeded defaults for property {property_obj.code} - {property_obj.name}'
                )
            )