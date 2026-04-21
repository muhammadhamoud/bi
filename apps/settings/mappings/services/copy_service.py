from dataclasses import dataclass
from typing import Dict

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.properties.core.models import Property
from apps.settings.mappings.services import MAPPING_DOMAIN_REGISTRY


@dataclass
class CopyStats:
    groups_created: int = 0
    groups_updated: int = 0
    groups_skipped: int = 0

    categories_created: int = 0
    categories_updated: int = 0
    categories_skipped: int = 0

    mappings_created: int = 0
    mappings_updated: int = 0
    mappings_skipped: int = 0

    details_created: int = 0
    details_updated: int = 0
    details_skipped: int = 0


class MappingCopyService:
    def __init__(
        self,
        *,
        domain_key: str,
        source_property: Property,
        target_property: Property,
        copy_groups: bool = True,
        copy_categories: bool = True,
        copy_mappings: bool = True,
        copy_details: bool = False,
        mode: str = "skip",
    ):
        self.domain_key = domain_key
        self.source_property = source_property
        self.target_property = target_property
        self.copy_groups = copy_groups
        self.copy_categories = copy_categories
        self.copy_mappings = copy_mappings
        self.copy_details = copy_details
        self.mode = mode

        self.stats = CopyStats()
        self.group_map: Dict[int, object] = {}
        self.category_map: Dict[int, object] = {}
        self.mapping_map: Dict[int, object] = {}

        if domain_key not in MAPPING_DOMAIN_REGISTRY:
            raise ValidationError(f"Unknown mapping domain: {domain_key}")

        self.config = MAPPING_DOMAIN_REGISTRY[domain_key]

        if self.source_property.pk == self.target_property.pk:
            raise ValidationError("Source and target property cannot be the same.")

    @transaction.atomic
    def execute(self):
        if self.copy_groups and self.config.get("has_group"):
            self._copy_groups()

        if self.copy_categories and self.config.get("has_category"):
            self._copy_categories()

        if self.copy_mappings:
            self._copy_mappings()

        if self.copy_details and self.config.get("detail_model"):
            self._copy_details()

        return self.stats

    def _copy_groups(self):
        model = self.config.get("group_model")
        if not model:
            return

        source_groups = model.objects.filter(property=self.source_property).order_by("sort_order", "name")

        for source in source_groups:
            target = model.objects.filter(property=self.target_property, code=source.code).first()

            if target:
                if self.mode == "update":
                    self._copy_common_fields(source, target)
                    target.save()
                    self.stats.groups_updated += 1
                else:
                    self.stats.groups_skipped += 1
            else:
                target = model.objects.create(
                    property=self.target_property,
                    code=source.code,
                    name=source.name,
                    color=getattr(source, "color", None),
                    icon=getattr(source, "icon", None),
                    image=getattr(source, "image", None),
                    description=getattr(source, "description", None),
                    sort_order=getattr(source, "sort_order", 0),
                    is_active=getattr(source, "is_active", True),
                )
                self.stats.groups_created += 1

            self.group_map[source.pk] = target

    def _copy_categories(self):
        model = self.config.get("category_model")
        if not model:
            return

        model_field_names = {f.name for f in model._meta.fields}
        source_categories = model.objects.filter(property=self.source_property).order_by("sort_order", "name")

        if "group" in model_field_names:
            source_categories = source_categories.select_related("group")

        for source in source_categories:
            target = model.objects.filter(property=self.target_property, code=source.code).first()

            target_group = None
            if "group" in model_field_names and getattr(source, "group_id", None):
                target_group = self.group_map.get(source.group_id)
                if not target_group and self.config.get("group_model"):
                    target_group = self.config["group_model"].objects.filter(
                        property=self.target_property,
                        code=source.group.code,
                    ).first()

            if target:
                if self.mode == "update":
                    target.name = source.name
                    target.description = getattr(source, "description", None)
                    target.sort_order = getattr(source, "sort_order", 0)
                    target.is_active = getattr(source, "is_active", True)

                    if "group" in model_field_names:
                        target.group = target_group

                    target.save()
                    self.stats.categories_updated += 1
                else:
                    self.stats.categories_skipped += 1
            else:
                create_kwargs = {
                    "property": self.target_property,
                    "code": source.code,
                    "name": source.name,
                    "description": getattr(source, "description", None),
                    "sort_order": getattr(source, "sort_order", 0),
                    "is_active": getattr(source, "is_active", True),
                }

                if "group" in model_field_names:
                    create_kwargs["group"] = target_group

                target = model.objects.create(**create_kwargs)
                self.stats.categories_created += 1

            self.category_map[source.pk] = target

    def _copy_mappings(self):
        model = self.config["mapping_model"]

        select_related_fields = []
        model_field_names = {f.name for f in model._meta.fields}

        if self.config.get("has_group") and "group" in model_field_names:
            select_related_fields.append("group")

        if self.config.get("has_category") and "category" in model_field_names:
            select_related_fields.append("category")

        source_queryset = model.objects.filter(property=self.source_property)

        if select_related_fields:
            source_queryset = source_queryset.select_related(*select_related_fields)

        for source in source_queryset:
            target = model.objects.filter(property=self.target_property, code=source.code).first()

            target_group = None
            target_category = None

            if "group" in model_field_names and getattr(source, "group_id", None):
                target_group = self.group_map.get(source.group_id)
                if not target_group and self.config.get("group_model"):
                    target_group = self.config["group_model"].objects.filter(
                        property=self.target_property,
                        code=source.group.code,
                    ).first()

            if "category" in model_field_names and getattr(source, "category_id", None):
                target_category = self.category_map.get(source.category_id)
                if not target_category and self.config.get("category_model"):
                    target_category = self.config["category_model"].objects.filter(
                        property=self.target_property,
                        code=source.category.code,
                    ).first()

            if target:
                if self.mode == "update":
                    self._copy_mapping_fields(source, target, target_group, target_category)
                    target.save()
                    self.stats.mappings_updated += 1
                else:
                    self.stats.mappings_skipped += 1
            else:
                create_kwargs = {
                    "property": self.target_property,
                    "code": source.code,
                    "name": source.name,
                    "description": getattr(source, "description", None),
                    "sort_order": getattr(source, "sort_order", 0),
                    "is_active": getattr(source, "is_active", True),
                }

                if "group" in model_field_names:
                    create_kwargs["group"] = target_group

                if "category" in model_field_names:
                    create_kwargs["category"] = target_category

                target = model.objects.create(**create_kwargs)
                self.stats.mappings_created += 1

            self.mapping_map[source.pk] = target

    def _copy_details(self):
        detail_model = self.config.get("detail_model")
        if not detail_model:
            return

        source_details = detail_model.objects.filter(
            property=self.source_property
        )

        detail_field_names = {f.name for f in detail_model._meta.fields}

        select_related_fields = []
        if "mapping" in detail_field_names:
            select_related_fields.append("mapping")
        if "category" in detail_field_names:
            select_related_fields.append("category")
        if "group" in detail_field_names:
            select_related_fields.append("group")

        if select_related_fields:
            source_details = source_details.select_related(*select_related_fields)

        for source in source_details:
            target_mapping = None
            if "mapping" in detail_field_names and getattr(source, "mapping_id", None):
                target_mapping = self.mapping_map.get(source.mapping_id)

            lookup = {}

            # Use the actual uniqueness pattern of the model
            if "property" in detail_field_names:
                lookup["property"] = self.target_property

            if hasattr(source, "code") and source.code:
                lookup["code"] = source.code
            elif hasattr(source, "value") and source.value:
                lookup["value"] = source.value
            elif hasattr(source, "name") and source.name:
                lookup["name"] = source.name
            else:
                continue

            # If the model does not have property-level uniqueness, fall back to mapping-level match
            if "property" not in detail_field_names and "mapping" in detail_field_names:
                if not target_mapping:
                    continue
                lookup["mapping"] = target_mapping

            target = detail_model.objects.filter(**lookup).first()

            if target:
                if self.mode == "update":
                    self._copy_detail_fields(source, target, target_mapping=target_mapping)
                    target.save()
                    self.stats.details_updated += 1
                else:
                    self.stats.details_skipped += 1
            else:
                create_kwargs = {}

                for field in detail_model._meta.fields:
                    field_name = field.name
                    if field_name == "id":
                        continue
                    if field_name == "property":
                        create_kwargs["property"] = self.target_property
                        continue
                    if field_name == "mapping":
                        create_kwargs["mapping"] = target_mapping
                        continue

                    if hasattr(source, field_name):
                        create_kwargs[field_name] = getattr(source, field_name)

                detail_model.objects.create(**create_kwargs)
                self.stats.details_created += 1

    def _copy_common_fields(self, source, target):
        for field in ("name", "color", "icon", "image", "description", "sort_order", "is_active"):
            if hasattr(source, field) and hasattr(target, field):
                setattr(target, field, getattr(source, field))

    def _copy_mapping_fields(self, source, target, target_group=None, target_category=None):
        for field in ("name", "description", "sort_order", "is_active"):
            if hasattr(source, field) and hasattr(target, field):
                setattr(target, field, getattr(source, field))

        target_field_names = {f.name for f in target._meta.fields}

        if "group" in target_field_names:
            target.group = target_group

        if "category" in target_field_names:
            target.category = target_category

    def _copy_detail_fields(self, source, target, target_mapping=None):
        for field in target._meta.fields:
            field_name = field.name

            if field_name == "id":
                continue

            if field_name == "property":
                target.property = self.target_property
                continue

            if field_name == "mapping":
                target.mapping = target_mapping
                continue

            if hasattr(source, field_name):
                setattr(target, field_name, getattr(source, field_name))