# apps/settings/mappings/services/room_type_defaults.py

from django.db import transaction

from apps.settings.mappings.models import (
    RoomTypeCategory,
    RoomTypeGroup,
    RoomTypeMapping,
)

DEFAULT_ROOM_TYPE_STRUCTURE = [
    # Guest Rooms
    {
        "mapping_code": "STD",
        "mapping_name": "Standard Room",
        "category_code": "STD",
        "category_name": "Standard",
        "group_code": "GRS",
        "group_name": "Guest Rooms",
    },
    {
        "mapping_code": "DLX",
        "mapping_name": "Deluxe Room",
        "category_code": "DLX",
        "category_name": "Deluxe",
        "group_code": "GRS",
        "group_name": "Guest Rooms",
    },

    # Premium Rooms
    {
        "mapping_code": "SUP",
        "mapping_name": "Superior Room",
        "category_code": "SUP",
        "category_name": "Superior",
        "group_code": "PRM",
        "group_name": "Premium Rooms",
    },
    {
        "mapping_code": "PRM",
        "mapping_name": "Premium Room",
        "category_code": "PRM",
        "category_name": "Premium",
        "group_code": "PRM",
        "group_name": "Premium Rooms",
    },

    # Club Executive Rooms
    {
        "mapping_code": "CLB",
        "mapping_name": "Club Room",
        "category_code": "CLB",
        "category_name": "Club Room",
        "group_code": "EXE",
        "group_name": "Club Executive Rooms",
    },
    {
        "mapping_code": "EXE",
        "mapping_name": "Executive Room",
        "category_code": "EXE",
        "category_name": "Executive Room",
        "group_code": "EXE",
        "group_name": "Club Executive Rooms",
    },

    # Suites
    {
        "mapping_code": "JSU",
        "mapping_name": "Junior Suite",
        "category_code": "SSU",
        "category_name": "Smaller Suites",
        "group_code": "STE",
        "group_name": "Suites",
    },
    {
        "mapping_code": "STE",
        "mapping_name": "Suite",
        "category_code": "SSU",
        "category_name": "Smaller Suites",
        "group_code": "STE",
        "group_name": "Suites",
    },
    {
        "mapping_code": "CSU",
        "mapping_name": "Club Suite",
        "category_code": "CSU",
        "category_name": "Club Suites",
        "group_code": "STE",
        "group_name": "Suites",
    },

    # Villa
    {
        "mapping_code": "VIL",
        "mapping_name": "Villa",
        "category_code": "VIL",
        "category_name": "Villa",
        "group_code": "VIL",
        "group_name": "Villa",
    },
]

APARTMENT_ROOM_TYPE_STRUCTURE = [
    {
        "mapping_code": "APT",
        "mapping_name": "Apartment",
        "category_code": "APT",
        "category_name": "Apartment",
        "group_code": "APT",
        "group_name": "Apartments",
    }
]


def get_default_room_type_structure(include_apartments=False):
    structure = list(DEFAULT_ROOM_TYPE_STRUCTURE)
    if include_apartments:
        structure.extend(APARTMENT_ROOM_TYPE_STRUCTURE)
    return structure


@transaction.atomic
def seed_default_room_types_for_property(property_obj, actor=None, include_apartments=False):
    structure = get_default_room_type_structure(include_apartments=include_apartments)

    group_cache = {}
    category_cache = {}

    unique_groups = list(
        dict.fromkeys((row["group_code"], row["group_name"]) for row in structure)
    )
    for group_index, (group_code, group_name) in enumerate(unique_groups, start=1):
        group, _ = RoomTypeGroup.objects.get_or_create(
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
        category, _ = RoomTypeCategory.objects.get_or_create(
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
        mapping, _ = RoomTypeMapping.objects.get_or_create(
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


