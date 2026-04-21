from django.db import transaction

from apps.settings.mappings.models import (
    OriginCategory,
    OriginGroup,
    OriginMapping,
)

DEFAULT_ORIGIN_STRUCTURE = [
    # Direct / Brand.com
    {
        "mapping_code": "WEB",
        "mapping_name": "Brand.com",
        "category_code": "BRC",
        "category_name": "Brand.com",
        "group_code": "DIR",
        "group_name": "Direct",
    },

    # Direct / Direct Hotel
    {
        "mapping_code": "PROP",
        "mapping_name": "Property",
        "category_code": "DHT",
        "category_name": "Direct Hotel",
        "group_code": "DIR",
        "group_name": "Direct",
    },
    {
        "mapping_code": "PMS",
        "mapping_name": "PMS",
        "category_code": "DHT",
        "category_name": "Direct Hotel",
        "group_code": "DIR",
        "group_name": "Direct",
    },
    {
        "mapping_code": "IHOS",
        "mapping_name": "IHOS",
        "category_code": "DHT",
        "category_name": "Direct Hotel",
        "group_code": "DIR",
        "group_name": "Direct",
    },
    {
        "mapping_code": "CALLHOTEL",
        "mapping_name": "Telephone",
        "category_code": "DHT",
        "category_name": "Direct Hotel",
        "group_code": "DIR",
        "group_name": "Direct",
    },
    {
        "mapping_code": "CALLCTR",
        "mapping_name": "Call Center",
        "category_code": "DHT",
        "category_name": "Direct Hotel",
        "group_code": "DIR",
        "group_name": "Direct",
    },
    {
        "mapping_code": "EM",
        "mapping_name": "Email",
        "category_code": "DHT",
        "category_name": "Direct Hotel",
        "group_code": "DIR",
        "group_name": "Direct",
    },
    {
        "mapping_code": "WAK",
        "mapping_name": "Walkin",
        "category_code": "DHT",
        "category_name": "Direct Hotel",
        "group_code": "DIR",
        "group_name": "Direct",
    },

    # Direct / Voice
    {
        "mapping_code": "CRO",
        "mapping_name": "CRO/VOICE",
        "category_code": "VOI",
        "category_name": "Voice",
        "group_code": "DIR",
        "group_name": "Direct",
    },

    # Direct / Group
    {
        "mapping_code": "RL",
        "mapping_name": "Group",
        "category_code": "GRP",
        "category_name": "Group",
        "group_code": "DIR",
        "group_name": "Direct",
    },
    {
        "mapping_code": "WEBGRP",
        "mapping_name": "Web Group",
        "category_code": "GRP",
        "category_name": "Group",
        "group_code": "DIR",
        "group_name": "Direct",
    },

    # Direct / Sales
    {
        "mapping_code": "SALE",
        "mapping_name": "Sales",
        "category_code": "SAL",
        "category_name": "Sales",
        "group_code": "DIR",
        "group_name": "Direct",
    },

    # Indirect / OTA
    {
        "mapping_code": "BOOKINGDC",
        "mapping_name": "Booking.com",
        "category_code": "OTA",
        "category_name": "Online Travel Agencies",
        "group_code": "IND",
        "group_name": "Indirect",
    },
    {
        "mapping_code": "EXPDC",
        "mapping_name": "Expedia.com",
        "category_code": "OTA",
        "category_name": "Online Travel Agencies",
        "group_code": "IND",
        "group_name": "Indirect",
    },
    {
        "mapping_code": "CTRIPDC",
        "mapping_name": "Ctrip.com",
        "category_code": "OTA",
        "category_name": "Online Travel Agencies",
        "group_code": "IND",
        "group_name": "Indirect",
    },
    {
        "mapping_code": "OTT",
        "mapping_name": "Other OTAs",
        "category_code": "OTA",
        "category_name": "Online Travel Agencies",
        "group_code": "IND",
        "group_name": "Indirect",
    },

    # Indirect / GDS
    {
        "mapping_code": "AMADEUS",
        "mapping_name": "Amadeus",
        "category_code": "GDS",
        "category_name": "Global Distribution Systems",
        "group_code": "IND",
        "group_name": "Indirect",
    },
    {
        "mapping_code": "SABRE",
        "mapping_name": "Sabre",
        "category_code": "GDS",
        "category_name": "Global Distribution Systems",
        "group_code": "IND",
        "group_name": "Indirect",
    },
    {
        "mapping_code": "GALLILEO",
        "mapping_name": "Gallileo",
        "category_code": "GDS",
        "category_name": "Global Distribution Systems",
        "group_code": "IND",
        "group_name": "Indirect",
    },
    {
        "mapping_code": "WORLDSPAN",
        "mapping_name": "Worldspan",
        "category_code": "GDS",
        "category_name": "Global Distribution Systems",
        "group_code": "IND",
        "group_name": "Indirect",
    },

    # System Contribution / Wholesale and Travel Web
    {
        "mapping_code": "WDY",
        "mapping_name": "Dynamic Wholesaler",
        "category_code": "WHL",
        "category_name": "Wholesale and Travel Web",
        "group_code": "SYS",
        "group_name": "System Contribution",
    },
    {
        "mapping_code": "WEBTA",
        "mapping_name": "Web Travel Agent",
        "category_code": "WHL",
        "category_name": "Wholesale and Travel Web",
        "group_code": "SYS",
        "group_name": "System Contribution",
    },
    {
        "mapping_code": "TWN",
        "mapping_name": "Travel Web Net Rate",
        "category_code": "WHL",
        "category_name": "Wholesale and Travel Web",
        "group_code": "SYS",
        "group_name": "System Contribution",
    },
    {
        "mapping_code": "TRAVELWEB",
        "mapping_name": "TravelWeb",
        "category_code": "WHL",
        "category_name": "Wholesale and Travel Web",
        "group_code": "SYS",
        "group_name": "System Contribution",
    },
    {
        "mapping_code": "EML",
        "mapping_name": "Email",
        "category_code": "WHL",
        "category_name": "Wholesale and Travel Web",
        "group_code": "SYS",
        "group_name": "System Contribution",
    },
]

def get_default_origin_structure():
    return list(DEFAULT_ORIGIN_STRUCTURE)


@transaction.atomic
def seed_default_origins_for_property(property_obj, actor=None):
    structure = get_default_origin_structure()

    group_cache = {}
    category_cache = {}

    unique_groups = list(
        dict.fromkeys((row["group_code"], row["group_name"]) for row in structure)
    )
    for group_index, (group_code, group_name) in enumerate(unique_groups, start=1):
        group, _ = OriginGroup.objects.get_or_create(
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
    for category_index, (category_code, category_name, group_code) in enumerate(
        unique_categories,
        start=1,
    ):
        category_group = group_cache[group_code]
        category, _ = OriginCategory.objects.get_or_create(
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
        mapping, _ = OriginMapping.objects.get_or_create(
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