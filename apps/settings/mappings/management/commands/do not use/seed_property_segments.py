# apps/settings/mappings/management/commands/seed_property_segments.py

from django.core.management.base import BaseCommand, CommandError

from apps.properties.core.models import Property
from bi.apps.settings.mappings.data_dontuse.segment_defaults import seed_default_segments_for_property


class Command(BaseCommand):
    help = "Seed default segment groups, categories, and segments for a property."

    def add_arguments(self, parser):
        parser.add_argument("--property-id", type=int, required=True)

    def handle(self, *args, **options):
        property_id = options["property_id"]

        try:
            property_obj = Property.objects.get(pk=property_id)
        except Property.DoesNotExist as exc:
            raise CommandError(f"Property {property_id} does not exist.") from exc

        seed_default_segments_for_property(property_obj=property_obj)
        self.stdout.write(
            self.style.SUCCESS(
                f"Default segments seeded successfully for property {property_obj.pk} - {property_obj.name}"
            )
        )