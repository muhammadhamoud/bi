from __future__ import annotations

from django.db import transaction

from apps.settings.mappings.services.default_registry import (
    DEFAULT_SEED_REGISTRY,
    get_seed_registry_item,
    load_seed_module,
)
from apps.settings.mappings.services.default_seed_engine import seed_hierarchy


@transaction.atomic
def seed_default_domain_for_property(
    *,
    property_obj,
    domain_key: str,
    actor=None,
    include_apartments: bool = False,
):
    registry_item = get_seed_registry_item(domain_key)
    module = load_seed_module(domain_key)

    if registry_item.custom_seeder:
        return registry_item.custom_seeder(
            property_obj=property_obj,
            actor=actor,
            include_apartments=include_apartments,
        )

    structure = registry_item.structure_getter(
        module,
        include_apartments=include_apartments,
    )

    return seed_hierarchy(
        property_obj=property_obj,
        actor=actor,
        structure=structure,
        plan=registry_item.plan,
    )


@transaction.atomic
def seed_default_mappings_for_property(
    property_obj,
    actor=None,
    domains: list[str] | tuple[str, ...] | None = None,
    include_apartments: bool = False,
):
    domain_keys = list(domains or DEFAULT_SEED_REGISTRY.keys())

    for domain_key in domain_keys:
        seed_default_domain_for_property(
            property_obj=property_obj,
            domain_key=domain_key,
            actor=actor,
            include_apartments=include_apartments,
        )
