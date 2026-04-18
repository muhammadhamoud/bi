# apps/settings/mappings/management/commands/flush_mapping_family.py

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.properties.core.models import Property


# Examples:
# python manage.py flush_mapping_family --model Package --property-id 1000
# python manage.py flush_mapping_family --model RoomType --property-code P6
# python manage.py flush_mapping_family --model Segment --all
# python manage.py flush_mapping_family --model Package --property-id 1000 --dry-run


class Command(BaseCommand):
    help = (
        "Flush mapping groups, categories, mappings, and optionally details "
        "for a given mapping family and one or more properties."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--model",
            type=str,
            required=True,
            help="Base model family name, e.g. Package, RoomType, Segment.",
        )
        parser.add_argument(
            "--property-id",
            type=int,
            nargs="*",
            help="One or more property IDs.",
        )
        parser.add_argument(
            "--property-code",
            type=str,
            nargs="*",
            help="One or more property codes.",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Flush for all properties.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without deleting anything.",
        )
        parser.add_argument(
            "--include-details",
            action="store_true",
            help="Also delete detail records, e.g. PackageDetail, RoomTypeDetail.",
        )

    def get_properties(self, options):
        property_ids = options.get("property_id") or []
        property_codes = options.get("property_code") or []
        flush_all = options.get("all", False)

        queryset = Property.objects.all()

        if flush_all:
            properties = queryset
        elif property_ids:
            properties = queryset.filter(id__in=property_ids)
        elif property_codes:
            properties = queryset.filter(code__in=property_codes)
        else:
            raise CommandError("Provide --all, --property-id, or --property-code.")

        if not properties.exists():
            raise CommandError("No matching properties found.")

        return properties.order_by("id")

    def find_model_by_name(self, model_name):
        matches = []

        for model in apps.get_models():
            if model.__name__.lower() == model_name.lower():
                matches.append(model)

        if not matches:
            raise CommandError(f"Model not found: {model_name}")

        if len(matches) > 1:
            labels = ", ".join(f"{m._meta.app_label}.{m.__name__}" for m in matches)
            raise CommandError(
                f"Multiple models found for {model_name}: {labels}. "
                f"Rename the command logic or narrow the search."
            )

        return matches[0]

    def get_model_family(self, base_name, include_details=False):
        group_model = self.find_model_by_name(f"{base_name}Group")
        category_model = self.find_model_by_name(f"{base_name}Category")
        mapping_model = self.find_model_by_name(f"{base_name}Mapping")
        detail_model = None

        if include_details:
            try:
                detail_model = self.find_model_by_name(f"{base_name}Detail")
            except CommandError:
                detail_model = None

        return group_model, category_model, mapping_model, detail_model

    @transaction.atomic
    def handle(self, *args, **options):
        base_name = (options.get("model") or "").strip()
        dry_run = options.get("dry_run", False)
        include_details = options.get("include_details", False)

        if not base_name:
            raise CommandError("Provide --model, e.g. --model Package")

        group_model, category_model, mapping_model, detail_model = self.get_model_family(
            base_name=base_name,
            include_details=include_details,
        )

        properties = self.get_properties(options)

        for property_obj in properties:
            detail_qs = detail_model.objects.filter(property=property_obj) if detail_model else None
            mapping_qs = mapping_model.objects.filter(property=property_obj)
            category_qs = category_model.objects.filter(property=property_obj)
            group_qs = group_model.objects.filter(property=property_obj)

            detail_count = detail_qs.count() if detail_qs is not None else 0
            mapping_count = mapping_qs.count()
            category_count = category_qs.count()
            group_count = group_qs.count()

            if dry_run:
                message = (
                    f"[DRY RUN] {base_name} | {property_obj.code} - {property_obj.name} | "
                    f"would delete "
                )
                if detail_qs is not None:
                    message += f"{detail_count} details, "
                message += (
                    f"{mapping_count} mappings, "
                    f"{category_count} categories, "
                    f"{group_count} groups"
                )
                self.stdout.write(self.style.WARNING(message))
                continue

            deleted_details = detail_qs.delete()[0] if detail_qs is not None else 0
            deleted_mappings = mapping_qs.delete()[0]
            deleted_categories = category_qs.delete()[0]
            deleted_groups = group_qs.delete()[0]

            message = (
                f"Flushed {base_name} for property {property_obj.code} - {property_obj.name} | "
            )
            if detail_qs is not None:
                message += f"deleted details={deleted_details}, "
            message += (
                f"mappings={deleted_mappings}, "
                f"categories={deleted_categories}, "
                f"groups={deleted_groups}"
            )

            self.stdout.write(self.style.SUCCESS(message))