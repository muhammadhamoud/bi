from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from django.db import transaction


@dataclass(frozen=True)
class LevelConfig:
    model: Any
    code_field: str = "code"
    name_field: str = "name"
    parent_field: str | None = None


@dataclass(frozen=True)
class SeedPlan:
    group: LevelConfig | None = None
    category: LevelConfig | None = None
    mapping: LevelConfig | None = None
    detail: LevelConfig | None = None

    group_key: str = "group_code"
    group_name_key: str = "group_name"

    category_key: str = "category_code"
    category_name_key: str = "category_name"
    category_parent_key: str = "group_code"

    mapping_key: str = "mapping_code"
    mapping_name_key: str = "mapping_name"
    mapping_parent_key: str = "category_code"

    detail_key: str = "detail_code"
    detail_name_key: str = "detail_name"

    group_rows_getter: Callable[[list[dict]], list[tuple]] | None = None
    category_rows_getter: Callable[[list[dict]], list[tuple]] | None = None
    mapping_parent_getter: Callable[[dict, dict, dict], Any] | None = None
    detail_parent_getter: Callable[[dict, dict, dict, dict], Any] | None = None
    detail_extra_updates_getter: Callable[[dict], dict] | None = None


def _base_defaults(
    *,
    name: str,
    sort_order: int,
    actor=None,
    extra: dict | None = None,
) -> dict:
    values = {
        "name": name,
        "sort_order": sort_order,
        "is_active": True,
        "created_by": actor,
        "updated_by": actor,
    }
    if extra:
        values.update(extra)
    return values


def sync_seed_instance(
    *,
    model,
    property_obj,
    code: str,
    sort_order: int,
    actor=None,
    code_field: str = "code",
    name_field: str = "name",
    name: str | None = None,
    parent_field: str | None = None,
    parent_obj=None,
    extra_defaults: dict | None = None,
    extra_updates: dict | None = None,
):
    lookup = {
        "property": property_obj,
        code_field: code,
    }

    defaults = _base_defaults(
        name=name or code,
        sort_order=sort_order,
        actor=actor,
        extra=extra_defaults,
    )

    if parent_field and parent_obj is not None:
        defaults[parent_field] = parent_obj

    instance, _ = model.objects.get_or_create(
        **lookup,
        defaults=defaults,
    )

    changed = False

    if name is not None and getattr(instance, name_field) != name:
        setattr(instance, name_field, name)
        changed = True

    if parent_field and parent_obj is not None:
        current_parent_id = getattr(instance, f"{parent_field}_id", None)
        if current_parent_id != parent_obj.id:
            setattr(instance, parent_field, parent_obj)
            changed = True

    if hasattr(instance, "sort_order") and instance.sort_order != sort_order:
        instance.sort_order = sort_order
        changed = True

    if hasattr(instance, "is_active") and not instance.is_active:
        instance.is_active = True
        changed = True

    if actor and hasattr(instance, "updated_by_id") and instance.updated_by_id != actor.id:
        instance.updated_by = actor
        changed = True

    if extra_updates:
        for field_name, value in extra_updates.items():
            if getattr(instance, field_name, None) != value:
                setattr(instance, field_name, value)
                changed = True

    if changed:
        instance.save()

    return instance


def ordered_unique_rows(rows: list[tuple]) -> list[tuple]:
    return list(dict.fromkeys(rows))


def _require_key(row: dict, key: str) -> Any:
    if key not in row:
        raise KeyError(
            f"Missing required key '{key}' in structure row. "
            f"Available keys: {sorted(row.keys())}"
        )
    return row[key]


@transaction.atomic
def seed_hierarchy(
    *,
    property_obj,
    structure: list[dict],
    plan: SeedPlan,
    actor=None,
):
    group_cache: dict[str, Any] = {}
    category_cache: dict[str, Any] = {}
    mapping_cache: dict[str, Any] = {}

    if plan.group:
        if plan.group_rows_getter:
            group_rows = plan.group_rows_getter(structure)
        else:
            group_rows = ordered_unique_rows(
                [
                    (
                        _require_key(row, plan.group_key),
                        _require_key(row, plan.group_name_key),
                    )
                    for row in structure
                ]
            )

        for index, (group_code, group_name) in enumerate(group_rows, start=1):
            group_cache[group_code] = sync_seed_instance(
                model=plan.group.model,
                property_obj=property_obj,
                code=group_code,
                sort_order=index,
                actor=actor,
                code_field=plan.group.code_field,
                name_field=plan.group.name_field,
                name=group_name,
            )

    if plan.category:
        if plan.category_rows_getter:
            category_rows = plan.category_rows_getter(structure)
        else:
            category_rows = ordered_unique_rows(
                [
                    (
                        _require_key(row, plan.category_key),
                        _require_key(row, plan.category_name_key),
                        _require_key(row, plan.category_parent_key),
                    )
                    for row in structure
                ]
            )

        for index, (category_code, category_name, group_code) in enumerate(category_rows, start=1):
            if group_code not in group_cache:
                raise KeyError(
                    f"Category parent group '{group_code}' not found in cache "
                    f"for property '{property_obj}'."
                )

            category_cache[category_code] = sync_seed_instance(
                model=plan.category.model,
                property_obj=property_obj,
                code=category_code,
                sort_order=index,
                actor=actor,
                code_field=plan.category.code_field,
                name_field=plan.category.name_field,
                name=category_name,
                parent_field=plan.category.parent_field,
                parent_obj=group_cache[group_code],
            )

    if plan.mapping:
        for index, row in enumerate(structure, start=1):
            mapping_code = _require_key(row, plan.mapping_key)
            mapping_name = _require_key(row, plan.mapping_name_key)

            if plan.mapping_parent_getter:
                parent_obj = plan.mapping_parent_getter(row, group_cache, category_cache)
            else:
                parent_key = _require_key(row, plan.mapping_parent_key)
                if parent_key not in category_cache:
                    raise KeyError(
                        f"Mapping parent category '{parent_key}' not found in cache "
                        f"for mapping '{mapping_code}'."
                    )
                parent_obj = category_cache[parent_key]

            mapping_cache[mapping_code] = sync_seed_instance(
                model=plan.mapping.model,
                property_obj=property_obj,
                code=mapping_code,
                sort_order=index,
                actor=actor,
                code_field=plan.mapping.code_field,
                name_field=plan.mapping.name_field,
                name=mapping_name,
                parent_field=plan.mapping.parent_field,
                parent_obj=parent_obj,
            )

    if plan.detail:
        if not plan.detail_parent_getter:
            raise ValueError("detail_parent_getter is required when plan.detail is configured.")

        for index, row in enumerate(structure, start=1):
            detail_code = _require_key(row, plan.detail_key)
            detail_name = _require_key(row, plan.detail_name_key)

            extra_updates = (
                plan.detail_extra_updates_getter(row)
                if plan.detail_extra_updates_getter
                else None
            )

            parent_obj = plan.detail_parent_getter(
                row,
                group_cache,
                category_cache,
                mapping_cache,
            )

            sync_seed_instance(
                model=plan.detail.model,
                property_obj=property_obj,
                code=detail_code,
                sort_order=index,
                actor=actor,
                code_field=plan.detail.code_field,
                name_field=plan.detail.name_field,
                name=detail_name,
                parent_field=plan.detail.parent_field,
                parent_obj=parent_obj,
                extra_updates=extra_updates,
            )