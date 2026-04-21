# apps/settings/mappings/services/package_defaults.py

from django.db import transaction

from apps.settings.mappings.models import (
    PackageCategory,
    PackageGroup,
    PackageMapping,
)

DEFAULT_PACKAGE_STRUCTURE = [
    # Meal Packages
    {
        "mapping_code": "BREAKFAST",
        "mapping_name": "Breakfast",
        "category_code": "BREAKFAST",
        "category_name": "Breakfast",
        "group_code": "MEAL",
        "group_name": "Meal Packages",
    },
    {
        "mapping_code": "LUNCH",
        "mapping_name": "Lunch",
        "category_code": "LUNCH",
        "category_name": "Lunch",
        "group_code": "MEAL",
        "group_name": "Meal Packages",
    },
    {
        "mapping_code": "DINNER",
        "mapping_name": "Dinner",
        "category_code": "DINNER",
        "category_name": "Dinner",
        "group_code": "MEAL",
        "group_name": "Meal Packages",
    },

    # Board Packages
    {
        "mapping_code": "HALFBOARD",
        "mapping_name": "Half Board",
        "category_code": "HALFBOARD",
        "category_name": "Half Board",
        "group_code": "BOARD",
        "group_name": "Board Packages",
    },
    {
        "mapping_code": "FULLBOARD",
        "mapping_name": "Full Board",
        "category_code": "FULLBOARD",
        "category_name": "Full Board",
        "group_code": "BOARD",
        "group_name": "Board Packages",
    },

    # Access and Benefits
    {
        "mapping_code": "CLUB_ACCESS",
        "mapping_name": "Club Access",
        "category_code": "CLUB_ACCESS",
        "category_name": "Club Access",
        "group_code": "ACCESS",
        "group_name": "Access and Benefits",
    },

    # Room Upselling Packages
    {
        "mapping_code": "ROOM_UPGRADE",
        "mapping_name": "Room Upgrade",
        "category_code": "ROOM_UPGRADE",
        "category_name": "Room Upgrade",
        "group_code": "ROOM_UPSELL",
        "group_name": "Room Upselling Packages",
    },

    # Stay Extras
    {
        "mapping_code": "STAY_EXTENSION",
        "mapping_name": "Stay Extension",
        "category_code": "STAY_EXTENSION",
        "category_name": "Stay Extension",
        "group_code": "STAY",
        "group_name": "Stay Extras",
    },

    # Events
    {
        "mapping_code": "GALA_DINNER",
        "mapping_name": "Gala Dinner",
        "category_code": "GALA_DINNER",
        "category_name": "Gala Dinner",
        "group_code": "EVENT",
        "group_name": "Event Packages",
    },
    {
        "mapping_code": "SEASONAL_EVENT",
        "mapping_name": "Seasonal Event",
        "category_code": "SEASONAL_EVENT",
        "category_name": "Seasonal Event",
        "group_code": "EVENT",
        "group_name": "Event Packages",
    },

    # Admin
    {
        "mapping_code": "ADMIN_CHARGE",
        "mapping_name": "Administrative Charge",
        "category_code": "ADMIN_CHARGE",
        "category_name": "Administrative Charge",
        "group_code": "ADMIN",
        "group_name": "Administrative and Internal",
    },
]

def get_default_package_structure():
    return list(DEFAULT_PACKAGE_STRUCTURE)


@transaction.atomic
def seed_default_packages_for_property(property_obj, actor=None):
    structure = get_default_package_structure()

    group_cache = {}
    category_cache = {}

    unique_groups = list(
        dict.fromkeys((row["group_code"], row["group_name"]) for row in structure)
    )
    for group_index, (group_code, group_name) in enumerate(unique_groups, start=1):
        group, _ = PackageGroup.objects.get_or_create(
            property=property_obj,
            code=group_code,
            defaults={
                "name": group_name,
                "sort_order": group_index,
                "is_active": True,
                "created_by": actor,
                "updated_by": actor,
            },
        )

        changed = False
        if group.name != group_name:
            group.name = group_name
            changed = True
        if group.sort_order != group_index:
            group.sort_order = group_index
            changed = True
        if not group.is_active:
            group.is_active = True
            changed = True
        if actor and group.updated_by_id != actor.id:
            group.updated_by = actor
            changed = True

        if changed:
            group.save()

        group_cache[group_code] = group

    unique_categories = list(
        dict.fromkeys(
            (row["category_code"], row["category_name"], row["group_code"])
            for row in structure
        )
    )
    for category_index, (category_code, category_name, group_code) in enumerate(unique_categories, start=1):
        category_group = group_cache[group_code]
        category, _ = PackageCategory.objects.get_or_create(
            property=property_obj,
            code=category_code,
            defaults={
                "name": category_name,
                "group": category_group,
                "sort_order": category_index,
                "is_active": True,
                "created_by": actor,
                "updated_by": actor,
            },
        )

        changed = False
        if category.name != category_name:
            category.name = category_name
            changed = True
        if category.group_id != category_group.id:
            category.group = category_group
            changed = True
        if category.sort_order != category_index:
            category.sort_order = category_index
            changed = True
        if not category.is_active:
            category.is_active = True
            changed = True
        if actor and category.updated_by_id != actor.id:
            category.updated_by = actor
            changed = True

        if changed:
            category.save()

        category_cache[category_code] = category

    for mapping_index, row in enumerate(structure, start=1):
        mapping_category = category_cache[row["category_code"]]
        mapping, _ = PackageMapping.objects.get_or_create(
            property=property_obj,
            code=row["mapping_code"],
            defaults={
                "name": row["mapping_name"],
                "category": mapping_category,
                "sort_order": mapping_index,
                "is_active": True,
                "created_by": actor,
                "updated_by": actor,
            },
        )

        changed = False
        if mapping.name != row["mapping_name"]:
            mapping.name = row["mapping_name"]
            changed = True
        if mapping.category_id != mapping_category.id:
            mapping.category = mapping_category
            changed = True
        if mapping.sort_order != mapping_index:
            mapping.sort_order = mapping_index
            changed = True
        if not mapping.is_active:
            mapping.is_active = True
            changed = True
        if actor and mapping.updated_by_id != actor.id:
            mapping.updated_by = actor
            changed = True

        if changed:
            mapping.save()