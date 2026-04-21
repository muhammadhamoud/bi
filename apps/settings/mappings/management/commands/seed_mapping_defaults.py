from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.properties.core.models import Property
from apps.settings.mappings.services.defaults import seed_default_mappings_for_property

# python manage.py seed_mapping_defaults --property-code P6 --domain booking_source
# python manage.py seed_mapping_defaults --property-id 1000 --domain booking_source company segment
# python manage.py seed_mapping_defaults --all-properties --all-domains
# python manage.py seed_mapping_defaults --property-code P6 --domain room_type --include-apartments

class Command(BaseCommand):
    help = "Seed mapping defaults for one or more properties."

    AVAILABLE_DOMAINS = [
        "booking_source",
        "company",
        "competitor",
        "country",
        "day_of_week",
        "loyalty",
        "origin",
        "package",
        "room_type",
        "segment",
        "travel_agency",
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            "--property-id",
            type=int,
            nargs="*",
            help="One or more property IDs to seed.",
        )
        parser.add_argument(
            "--property-code",
            type=str,
            nargs="*",
            help="One or more property codes to seed.",
        )
        parser.add_argument(
            "--all-properties",
            action="store_true",
            help="Seed all properties.",
        )
        parser.add_argument(
            "--domain",
            type=str,
            nargs="*",
            choices=self.AVAILABLE_DOMAINS,
            help="One or more domains to seed. If omitted with --all-domains, all supported domains are seeded.",
        )
        parser.add_argument(
            "--all-domains",
            action="store_true",
            help="Seed all supported domains.",
        )
        parser.add_argument(
            "--include-apartments",
            action="store_true",
            help="Include apartment room type defaults when seeding room_type.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        property_ids = options.get("property_id") or []
        property_codes = options.get("property_code") or []
        all_properties = options.get("all_properties", False)

        selected_domains = options.get("domain") or []
        all_domains = options.get("all_domains", False)
        include_apartments = options.get("include_apartments", False)

        queryset = Property.objects.all()

        if all_properties:
            properties = queryset
        elif property_ids:
            properties = queryset.filter(id__in=property_ids)
        elif property_codes:
            properties = queryset.filter(code__in=property_codes)
        else:
            raise CommandError(
                "Provide --all-properties, --property-id, or --property-code."
            )

        if not properties.exists():
            raise CommandError("No matching properties found.")

        if all_domains:
            domains = self.AVAILABLE_DOMAINS
        elif selected_domains:
            domains = selected_domains
        else:
            raise CommandError("Provide --domain or --all-domains.")

        for property_obj in properties.order_by("id"):
            seed_default_mappings_for_property(
                property_obj=property_obj,
                actor=None,
                domains=domains,
                include_apartments=include_apartments,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Seeded {', '.join(domains)} for property "
                    f"{property_obj.code} - {property_obj.name}"
                )
            )