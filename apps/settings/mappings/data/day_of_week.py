# apps/settings/mappings/services/day_of_week_defaults.py

from django.db import transaction

from apps.settings.mappings.models import DayOfWeekGroup, DayOfWeekMapping


DEFAULT_DAY_OF_WEEK_STRUCTURE = [
    {"day_code": "MON", "day_name": "Monday", "group_code": "WD", "group_name": "Weekday"},
    {"day_code": "TUE", "day_name": "Tuesday", "group_code": "WD", "group_name": "Weekday"},
    {"day_code": "WED", "day_name": "Wednesday", "group_code": "WD", "group_name": "Weekday"},
    {"day_code": "THU", "day_name": "Thursday", "group_code": "WD", "group_name": "Weekday"},
    {"day_code": "FRI", "day_name": "Friday", "group_code": "WD", "group_name": "Weekday"},
    {"day_code": "SAT", "day_name": "Saturday", "group_code": "WE", "group_name": "Weekend"},
    {"day_code": "SUN", "day_name": "Sunday", "group_code": "WE", "group_name": "Weekend"},
]


@transaction.atomic
def seed_default_day_of_week_for_property(property_obj, actor=None):
    group_cache = {}

    unique_groups = list(
        dict.fromkeys((row["group_code"], row["group_name"]) for row in DEFAULT_DAY_OF_WEEK_STRUCTURE)
    )

    for group_index, (group_code, group_name) in enumerate(unique_groups, start=1):
        group, _ = DayOfWeekGroup.objects.get_or_create(
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

    for mapping_index, row in enumerate(DEFAULT_DAY_OF_WEEK_STRUCTURE, start=1):
        mapping_group = group_cache[row["group_code"]]
        mapping, _ = DayOfWeekMapping.objects.get_or_create(
            property=property_obj,
            code=row["day_code"],
            defaults={
                "name": row["day_name"],
                "group": mapping_group,
                "sort_order": mapping_index,
                "is_active": True,
                "created_by": actor,
                "updated_by": actor,
            },
        )

        changed = False
        if mapping.name != row["day_name"]:
            mapping.name = row["day_name"]
            changed = True
        if mapping.group_id != mapping_group.id:
            mapping.group = mapping_group
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