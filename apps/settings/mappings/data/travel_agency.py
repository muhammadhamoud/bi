# apps/settings/mappings/services/travel_agency_defaults.py

from django.db import transaction

from apps.settings.mappings.models import (
    TravelAgentCategory,
    TravelAgentGroup,
    TravelAgentMapping,
)

DEFAULT_TRAVEL_AGENCY_STRUCTURE = [
    # Online Travel Agencies
    {
        "mapping_code": "OTA",
        "mapping_name": "Online Travel Agency",
        "category_code": "OTA",
        "category_name": "Online Travel Agencies",
        "group_code": "DIG",
        "group_name": "Digital Travel Channels",
    },
    {
        "mapping_code": "META",
        "mapping_name": "Metasearch Travel Platform",
        "category_code": "OTA",
        "category_name": "Online Travel Agencies",
        "group_code": "DIG",
        "group_name": "Digital Travel Channels",
    },

    # Traditional Agencies
    {
        "mapping_code": "RETAIL_TA",
        "mapping_name": "Retail Travel Agency",
        "category_code": "TRAD",
        "category_name": "Traditional Travel Agencies",
        "group_code": "OFF",
        "group_name": "Offline Travel Channels",
    },
    {
        "mapping_code": "WHOLESALE_TA",
        "mapping_name": "Wholesale Travel Agency",
        "category_code": "TRAD",
        "category_name": "Traditional Travel Agencies",
        "group_code": "OFF",
        "group_name": "Offline Travel Channels",
    },

    # Corporate Travel
    {
        "mapping_code": "TMC",
        "mapping_name": "Travel Management Company",
        "category_code": "CORP",
        "category_name": "Corporate Travel",
        "group_code": "BUS",
        "group_name": "Business Travel",
    },
    {
        "mapping_code": "CORP_TA",
        "mapping_name": "Corporate Travel Agency",
        "category_code": "CORP",
        "category_name": "Corporate Travel",
        "group_code": "BUS",
        "group_name": "Business Travel",
    },

    # Destination and Leisure
    {
        "mapping_code": "DMC",
        "mapping_name": "Destination Management Company",
        "category_code": "DMC",
        "category_name": "Destination Services",
        "group_code": "LEI",
        "group_name": "Leisure Travel",
    },
    {
        "mapping_code": "TOUR_OP",
        "mapping_name": "Tour Operator",
        "category_code": "DMC",
        "category_name": "Destination Services",
        "group_code": "LEI",
        "group_name": "Leisure Travel",
    },

    # Specialized Travel
    {
        "mapping_code": "MICE",
        "mapping_name": "MICE Travel Agency",
        "category_code": "SPEC",
        "category_name": "Specialized Travel",
        "group_code": "SPC",
        "group_name": "Specialized Travel Services",
    },
    {
        "mapping_code": "LUX_TA",
        "mapping_name": "Luxury Travel Agency",
        "category_code": "SPEC",
        "category_name": "Specialized Travel",
        "group_code": "SPC",
        "group_name": "Specialized Travel Services",
    },
    {
        "mapping_code": "UMRAH",
        "mapping_name": "Religious Travel Agency",
        "category_code": "SPEC",
        "category_name": "Specialized Travel",
        "group_code": "SPC",
        "group_name": "Specialized Travel Services",
    },
]


def get_default_travel_agency_structure():
    return list(DEFAULT_TRAVEL_AGENCY_STRUCTURE)


@transaction.atomic
def seed_default_travel_agencies_for_property(property_obj, actor=None):
    structure = get_default_travel_agency_structure()

    group_cache = {}
    category_cache = {}

    unique_groups = list(
        dict.fromkeys((row["group_code"], row["group_name"]) for row in structure)
    )
    for group_index, (group_code, group_name) in enumerate(unique_groups, start=1):
        group, _ = TravelAgentGroup.objects.get_or_create(
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
        category, _ = TravelAgentCategory.objects.get_or_create(
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
        mapping, _ = TravelAgentMapping.objects.get_or_create(
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