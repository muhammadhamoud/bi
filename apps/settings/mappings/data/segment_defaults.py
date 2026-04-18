# apps/settings/mappings/services/segment_defaults.py

from django.db import transaction

from apps.settings.mappings.models import SegmentCategory, SegmentGroup, SegmentMapping

DEFAULT_SEGMENT_STRUCTURE = [
    {"segment_code": "GCO", "segment_name": "Group Corporate", "category_code": "GRP", "category_name": "Group", "group_code": "GRP", "group_name": "Group"},
    {"segment_code": "GAS", "segment_name": "Group Association", "category_code": "GRP", "category_name": "Group", "group_code": "GRP", "group_name": "Group"},
    {"segment_code": "GOT", "segment_name": "Group Other", "category_code": "GRP", "category_name": "Group", "group_code": "GRP", "group_name": "Group"},
    {"segment_code": "GWH", "segment_name": "Group Tour series / Wholesale", "category_code": "GRP", "category_name": "Group", "group_code": "GRP", "group_name": "Group"},
    {"segment_code": "GGO", "segment_name": "Group Government", "category_code": "GRP", "category_name": "Group", "group_code": "GRP", "group_name": "Group"},
    {"segment_code": "GSP", "segment_name": "Group Sport", "category_code": "GRP", "category_name": "Group", "group_code": "GRP", "group_name": "Group"},
    {"segment_code": "GMP", "segment_name": "Group Complimentary", "category_code": "COM", "category_name": "Complimentary", "group_code": "COM", "group_name": "Complimentary"},
    {"segment_code": "CMP", "segment_name": "Complimentary", "category_code": "COM", "category_name": "Complimentary", "group_code": "COM", "group_name": "Complimentary"},
    {"segment_code": "HUS", "segment_name": "House Use", "category_code": "COM", "category_name": "Complimentary", "group_code": "COM", "group_name": "Complimentary"},
    {"segment_code": "CON", "segment_name": "Contract", "category_code": "CON", "category_name": "Contract", "group_code": "CON", "group_name": "Contract"},
    {"segment_code": "DISD", "segment_name": "Discount Deep > 20%", "category_code": "RED", "category_name": "Retail Discount", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "DISM", "segment_name": "Discount Medium < 20%", "category_code": "RED", "category_name": "Retail Discount", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "PKG", "segment_name": "Value Added Packages", "category_code": "PKG", "category_name": "Packages", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "ADP", "segment_name": "Prepay", "category_code": "ADP", "category_name": "Prepay", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "BEN", "segment_name": "Best Flexible Rate", "category_code": "RET", "category_name": "Retail", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "GOV", "segment_name": "Government", "category_code": "GOV", "category_name": "Government", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "NEGL", "segment_name": "Negotiated Global (LRA)", "category_code": "NEG", "category_name": "Negotiated", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "NEGN", "segment_name": "Negotiated Global (NLRA)", "category_code": "NEG", "category_name": "Negotiated", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "NELL", "segment_name": "Negotiated Local (LRA)", "category_code": "NEG", "category_name": "Negotiated", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "NELN", "segment_name": "Negotiated Local (NLRA)", "category_code": "NEG", "category_name": "Negotiated", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "NECON", "segment_name": "Negotiated Long Stayer", "category_code": "NEG", "category_name": "Negotiated", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "WHD", "segment_name": "Wholesale Dynamic", "category_code": "WHO", "category_name": "Wholesale", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "WHO", "segment_name": "Wholesale Static", "category_code": "WHO", "category_name": "Wholesale", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "ODC", "segment_name": "Other Discount", "category_code": "OTH", "category_name": "Other Discount", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "EMP", "segment_name": "Employees/Friends/Family", "category_code": "OTH", "category_name": "Other Discount", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "LOY", "segment_name": "Loyalty Redemption", "category_code": "LOY", "category_name": "Loyalty Redemption", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "QUA", "segment_name": "Qualified Others", "category_code": "OTH", "category_name": "Other Discount", "group_code": "TRA", "group_name": "Transient"},
    {"segment_code": "REB", "segment_name": "Rebates Revenue", "category_code": "ORV", "category_name": "Other Revenue", "group_code": "ORV", "group_name": "Other Revenue"},
    {"segment_code": "ONR", "segment_name": "Other Non-Revenue", "category_code": "ORV", "category_name": "Other Revenue", "group_code": "ORV", "group_name": "Other Revenue"},
    {"segment_code": "ORR", "segment_name": "Other Room Revenue", "category_code": "ORV", "category_name": "Other Revenue", "group_code": "ORV", "group_name": "Other Revenue"},
    {"segment_code": "UKN", "segment_name": "Unknown", "category_code": "UKN", "category_name": "Unknown", "group_code": "UKN", "group_name": "Unknown"},
]


@transaction.atomic
def seed_default_segments_for_property(property_obj, actor=None):
    group_cache = {}
    category_cache = {}

    unique_groups = list(
        dict.fromkeys((row["group_code"], row["group_name"]) for row in DEFAULT_SEGMENT_STRUCTURE)
    )
    for group_index, (group_code, group_name) in enumerate(unique_groups, start=1):
        group, _ = SegmentGroup.objects.get_or_create(
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
            for row in DEFAULT_SEGMENT_STRUCTURE
        )
    )
    for category_index, (category_code, category_name, group_code) in enumerate(unique_categories, start=1):
        category_group = group_cache[group_code]
        category, _ = SegmentCategory.objects.get_or_create(
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

    for segment_index, row in enumerate(DEFAULT_SEGMENT_STRUCTURE, start=1):
        segment_category = category_cache[row["category_code"]]
        segment, _ = SegmentMapping.objects.get_or_create(
            property=property_obj,
            code=row["segment_code"],
            defaults={
                "name": row["segment_name"],
                "category": segment_category,
                "sort_order": segment_index,
                "is_active": True,
                "created_by": actor,
                "updated_by": actor,
            },
        )

        changed = False
        if segment.name != row["segment_name"]:
            segment.name = row["segment_name"]
            changed = True
        if segment.category_id != segment_category.id:
            segment.category = segment_category
            changed = True
        if segment.sort_order != segment_index:
            segment.sort_order = segment_index
            changed = True
        if not segment.is_active:
            segment.is_active = True
            changed = True
        if actor and segment.updated_by_id != actor.id:
            segment.updated_by = actor
            changed = True

        if changed:
            segment.save()