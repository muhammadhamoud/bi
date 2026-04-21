from django.db import transaction

from apps.settings.mappings.models import (
    BookingSourceCategory,
    BookingSourceGroup,
    BookingSourceMapping,
)

DEFAULT_BOOKING_SOURCE_STRUCTURE = [
    # Global and Regional Sales
    {
        "mapping_code": "GSO",
        "mapping_name": "Global Sales Organization",
        "category_code": "GLOBAL_SALES",
        "category_name": "Global Sales",
        "group_code": "SALES",
        "group_name": "Sales Channels",
    },
    {
        "mapping_code": "ISO",
        "mapping_name": "RC ISO",
        "category_code": "GLOBAL_SALES",
        "category_name": "Global Sales",
        "group_code": "SALES",
        "group_name": "Sales Channels",
    },
    {
        "mapping_code": "MSL",
        "mapping_name": "Market Sales",
        "category_code": "REGIONAL_SALES",
        "category_name": "Regional Sales",
        "group_code": "SALES",
        "group_name": "Sales Channels",
    },
    {
        "mapping_code": "MSU",
        "mapping_name": "Market Sales/UK",
        "category_code": "REGIONAL_SALES",
        "category_name": "Regional Sales",
        "group_code": "SALES",
        "group_name": "Sales Channels",
    },
    {
        "mapping_code": "PRS",
        "mapping_name": "Property Sales",
        "category_code": "PROPERTY_SALES",
        "category_name": "Property Sales",
        "group_code": "SALES",
        "group_name": "Sales Channels",
    },
    {
        "mapping_code": "SEG",
        "mapping_name": "Segment Sales",
        "category_code": "SPECIALIZED_SALES",
        "category_name": "Specialized Sales",
        "group_code": "SALES",
        "group_name": "Sales Channels",
    },
    {
        "mapping_code": "TEL",
        "mapping_name": "Telesales",
        "category_code": "SPECIALIZED_SALES",
        "category_name": "Specialized Sales",
        "group_code": "SALES",
        "group_name": "Sales Channels",
    },
    {
        "mapping_code": "TER",
        "mapping_name": "Territory Sales",
        "category_code": "SPECIALIZED_SALES",
        "category_name": "Specialized Sales",
        "group_code": "SALES",
        "group_name": "Sales Channels",
    },

    # Group and Catering
    {
        "mapping_code": "ECN",
        "mapping_name": "EMEA Convention Network",
        "category_code": "GROUP_CATERING",
        "category_name": "Group and Catering",
        "group_code": "GROUP",
        "group_name": "Group Business",
    },
    {
        "mapping_code": "NCA",
        "mapping_name": "National Catering Accounts",
        "category_code": "GROUP_CATERING",
        "category_name": "Group and Catering",
        "group_code": "GROUP",
        "group_name": "Group Business",
    },
    {
        "mapping_code": "NGA",
        "mapping_name": "National Group Accounts",
        "category_code": "GROUP_CATERING",
        "category_name": "Group and Catering",
        "group_code": "GROUP",
        "group_name": "Group Business",
    },
    {
        "mapping_code": "NGS",
        "mapping_name": "National Group Sales",
        "category_code": "GROUP_CATERING",
        "category_name": "Group and Catering",
        "group_code": "GROUP",
        "group_name": "Group Business",
    },
    {
        "mapping_code": "QGR",
        "mapping_name": "QuickGroup Response Team",
        "category_code": "GROUP_CATERING",
        "category_name": "Group and Catering",
        "group_code": "GROUP",
        "group_name": "Group Business",
    },
    {
        "mapping_code": "EGD",
        "mapping_name": "EMEA Group Desk",
        "category_code": "GROUP_CATERING",
        "category_name": "Group and Catering",
        "group_code": "GROUP",
        "group_name": "Group Business",
    },
    {
        "mapping_code": "TCM",
        "mapping_name": "TCM Destination Sales",
        "category_code": "GROUP_CATERING",
        "category_name": "Group and Catering",
        "group_code": "GROUP",
        "group_name": "Group Business",
    },

    # Lead Referral and Development
    {
        "mapping_code": "LRM",
        "mapping_name": "MWLR (Midwest Lead Referral)",
        "category_code": "LEAD_REFERRAL",
        "category_name": "Lead Referral",
        "group_code": "BD",
        "group_name": "Business Development",
    },
    {
        "mapping_code": "LRN",
        "mapping_name": "NERLR (NE Region Lead Ref)",
        "category_code": "LEAD_REFERRAL",
        "category_name": "Lead Referral",
        "group_code": "BD",
        "group_name": "Business Development",
    },
    {
        "mapping_code": "LRW",
        "mapping_name": "WRLR (Western Region Lead Ref)",
        "category_code": "LEAD_REFERRAL",
        "category_name": "Lead Referral",
        "group_code": "BD",
        "group_name": "Business Development",
    },
    {
        "mapping_code": "GEN",
        "mapping_name": "General Sales Agent",
        "category_code": "BUSINESS_DEV",
        "category_name": "Business Development",
        "group_code": "BD",
        "group_name": "Business Development",
    },
    {
        "mapping_code": "BDS",
        "mapping_name": "Business Development - SFO",
        "category_code": "BUSINESS_DEV",
        "category_name": "Business Development",
        "group_code": "BD",
        "group_name": "Business Development",
    },
    {
        "mapping_code": "RBD",
        "mapping_name": "Renaissance Business Development",
        "category_code": "BUSINESS_DEV",
        "category_name": "Business Development",
        "group_code": "BD",
        "group_name": "Business Development",
    },

    # Reservations and Service Centers
    {
        "mapping_code": "SAL",
        "mapping_name": "Sales Center",
        "category_code": "SERVICE_CENTERS",
        "category_name": "Service Centers",
        "group_code": "RES",
        "group_name": "Reservations and Support",
    },
    {
        "mapping_code": "WOR",
        "mapping_name": "Worldwide Reservations",
        "category_code": "RESERVATIONS",
        "category_name": "Reservations",
        "group_code": "RES",
        "group_name": "Reservations and Support",
    },
    {
        "mapping_code": "ACS",
        "mapping_name": "Account Sales",
        "category_code": "SERVICE_CENTERS",
        "category_name": "Service Centers",
        "group_code": "RES",
        "group_name": "Reservations and Support",
    },

    # National Sales Offices
    {
        "mapping_code": "NSC",
        "mapping_name": "NSO China",
        "category_code": "NATIONAL_OFFICES",
        "category_name": "National Sales Offices",
        "group_code": "NSO",
        "group_name": "National Sales Offices",
    },
    {
        "mapping_code": "NSI",
        "mapping_name": "NSO India",
        "category_code": "NATIONAL_OFFICES",
        "category_name": "National Sales Offices",
        "group_code": "NSO",
        "group_name": "National Sales Offices",
    },
    {
        "mapping_code": "NSP",
        "mapping_name": "NSO Philippines",
        "category_code": "NATIONAL_OFFICES",
        "category_name": "National Sales Offices",
        "group_code": "NSO",
        "group_name": "National Sales Offices",
    },
    {
        "mapping_code": "NST",
        "mapping_name": "NST Germany",
        "category_code": "NATIONAL_OFFICES",
        "category_name": "National Sales Offices",
        "group_code": "NSO",
        "group_name": "National Sales Offices",
    },
    {
        "mapping_code": "NSL",
        "mapping_name": "NST Italy",
        "category_code": "NATIONAL_OFFICES",
        "category_name": "National Sales Offices",
        "group_code": "NSO",
        "group_name": "National Sales Offices",
    },
    {
        "mapping_code": "NSO",
        "mapping_name": "NST Poland",
        "category_code": "NATIONAL_OFFICES",
        "category_name": "National Sales Offices",
        "group_code": "NSO",
        "group_name": "National Sales Offices",
    },
    {
        "mapping_code": "NSS",
        "mapping_name": "NST South Africa",
        "category_code": "NATIONAL_OFFICES",
        "category_name": "National Sales Offices",
        "group_code": "NSO",
        "group_name": "National Sales Offices",
    },
    {
        "mapping_code": "NSK",
        "mapping_name": "NST Turkey",
        "category_code": "NATIONAL_OFFICES",
        "category_name": "National Sales Offices",
        "group_code": "NSO",
        "group_name": "National Sales Offices",
    },
    {
        "mapping_code": "NSU",
        "mapping_name": "NST UK",
        "category_code": "NATIONAL_OFFICES",
        "category_name": "National Sales Offices",
        "group_code": "NSO",
        "group_name": "National Sales Offices",
    },

    # Other / Special Channels
    {
        "mapping_code": "EVE",
        "mapping_name": "EventCom Technology",
        "category_code": "SPECIAL_CHANNELS",
        "category_name": "Special Channels",
        "group_code": "OTH",
        "group_name": "Other Channels",
    },
    {
        "mapping_code": "OSR",
        "mapping_name": "OSRN",
        "category_code": "SPECIAL_CHANNELS",
        "category_name": "Special Channels",
        "group_code": "OTH",
        "group_name": "Other Channels",
    },
    {
        "mapping_code": "SCO",
        "mapping_name": "SCORE",
        "category_code": "SPECIAL_CHANNELS",
        "category_name": "Special Channels",
        "group_code": "OTH",
        "group_name": "Other Channels",
    },
    {
        "mapping_code": "SER",
        "mapping_name": "SERSO",
        "category_code": "SPECIAL_CHANNELS",
        "category_name": "Special Channels",
        "group_code": "OTH",
        "group_name": "Other Channels",
    },
    {
        "mapping_code": "APC",
        "mapping_name": "APEC LPC",
        "category_code": "SPECIAL_CHANNELS",
        "category_name": "Special Channels",
        "group_code": "OTH",
        "group_name": "Other Channels",
    },
    {
        "mapping_code": "GCL",
        "mapping_name": "GC LPC",
        "category_code": "SPECIAL_CHANNELS",
        "category_name": "Special Channels",
        "group_code": "OTH",
        "group_name": "Other Channels",
    },
    {
        "mapping_code": "MAR",
        "mapping_name": "MARCAM",
        "category_code": "SPECIAL_CHANNELS",
        "category_name": "Special Channels",
        "group_code": "OTH",
        "group_name": "Other Channels",
    },
    {
        "mapping_code": "MIL",
        "mapping_name": "MI LEADS",
        "category_code": "SPECIAL_CHANNELS",
        "category_name": "Special Channels",
        "group_code": "OTH",
        "group_name": "Other Channels",
    },
]

def get_default_booking_source_structure():
    return list(DEFAULT_BOOKING_SOURCE_STRUCTURE)


@transaction.atomic
def seed_default_booking_sources_for_property(property_obj, actor=None):
    structure = get_default_booking_source_structure()

    group_cache = {}
    category_cache = {}

    unique_groups = list(
        dict.fromkeys((row["group_code"], row["group_name"]) for row in structure)
    )
    for group_index, (group_code, group_name) in enumerate(unique_groups, start=1):
        group, _ = BookingSourceGroup.objects.get_or_create(
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
        category, _ = BookingSourceCategory.objects.get_or_create(
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
        mapping, _ = BookingSourceMapping.objects.get_or_create(
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