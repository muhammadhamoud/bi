# apps/settings/mappings/services/loyalty_defaults.py

from django.db import transaction

from apps.settings.mappings.models import (
    LoyaltyCategory,
    LoyaltyGroup,
    LoyaltyMapping,
)

DEFAULT_LOYALTY_STRUCTURE = [
    {
        "mapping_code": "BASE",
        "mapping_name": "Base Member",
        "category_code": "BASE",
        "category_name": "Base Tier",
        "group_code": "LOY",
        "group_name": "Loyalty Membership",
    },
    {
        "mapping_code": "SILVER",
        "mapping_name": "Silver Member",
        "category_code": "ELITE",
        "category_name": "Elite Tier",
        "group_code": "LOY",
        "group_name": "Loyalty Membership",
    },
    {
        "mapping_code": "GOLD",
        "mapping_name": "Gold Member",
        "category_code": "ELITE",
        "category_name": "Elite Tier",
        "group_code": "LOY",
        "group_name": "Loyalty Membership",
    },
    {
        "mapping_code": "PLAT",
        "mapping_name": "Platinum Member",
        "category_code": "PREM",
        "category_name": "Premium Tier",
        "group_code": "LOY",
        "group_name": "Loyalty Membership",
    },
]


def get_default_loyalty_structure():
    return list(DEFAULT_LOYALTY_STRUCTURE)


@transaction.atomic
def seed_default_loyalties_for_property(property_obj, actor=None):
    structure = get_default_loyalty_structure()

    group_cache = {}
    category_cache = {}

    unique_groups = list(
        dict.fromkeys((row["group_code"], row["group_name"]) for row in structure)
    )
    for group_index, (group_code, group_name) in enumerate(unique_groups, start=1):
        group, _ = LoyaltyGroup.objects.get_or_create(
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
        category, _ = LoyaltyCategory.objects.get_or_create(
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
        mapping, _ = LoyaltyMapping.objects.get_or_create(
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