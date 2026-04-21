from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Callable

from apps.settings.mappings.models import (
    BookingSourceCategory,
    BookingSourceGroup,
    BookingSourceMapping,
    CompanyCategory,
    CompanyGroup,
    CompanyMapping,
    CompetitorCategory,
    CompetitorGroup,
    CompetitorMapping,
    DayOfWeekGroup,
    DayOfWeekMapping,
    GuestCountryCategory,
    GuestCountryDetail,
    GuestCountryGroup,
    GuestCountryMapping,
    LoyaltyCategory,
    LoyaltyGroup,
    LoyaltyMapping,
    OriginCategory,
    OriginGroup,
    OriginMapping,
    PackageCategory,
    PackageGroup,
    PackageMapping,
    RoomTypeCategory,
    RoomTypeGroup,
    RoomTypeMapping,
    SegmentCategory,
    SegmentGroup,
    SegmentMapping,
    TravelAgentCategory,
    TravelAgentGroup,
    TravelAgentMapping,
)
from apps.settings.mappings.services.default_seed_engine import LevelConfig, SeedPlan


@dataclass(frozen=True)
class DomainRegistryItem:
    module_path: str
    structure_getter: Callable[..., list[dict]]
    plan: SeedPlan
    custom_seeder: Callable[..., None] | None = None


def standard_plan(group_model, category_model, mapping_model) -> SeedPlan:
    return SeedPlan(
        group=LevelConfig(model=group_model),
        category=LevelConfig(model=category_model, parent_field="group"),
        mapping=LevelConfig(model=mapping_model, parent_field="category"),
        group_key="group_code",
        group_name_key="group_name",
        category_key="category_code",
        category_name_key="category_name",
        category_parent_key="group_code",
        mapping_key="mapping_code",
        mapping_name_key="mapping_name",
        mapping_parent_key="category_code",
    )


def group_mapping_plan(
    group_model,
    mapping_model,
    *,
    mapping_key: str,
    mapping_name_key: str,
    mapping_parent_key: str = "group_code",
) -> SeedPlan:
    return SeedPlan(
        group=LevelConfig(model=group_model),
        mapping=LevelConfig(model=mapping_model, parent_field="group"),
        group_key="group_code",
        group_name_key="group_name",
        mapping_key=mapping_key,
        mapping_name_key=mapping_name_key,
        mapping_parent_key=mapping_parent_key,
        mapping_parent_getter=lambda row, group_cache, category_cache: group_cache[row[mapping_parent_key]],
    )


def build_country_structure(module) -> list[dict]:
    rows: list[dict] = []

    for row in module.DEFAULT_COUNTRY_STRUCTURE:
        category_key = module.get_country_category_key(row["country_name"])
        category_config = module.CATEGORIES[category_key]
        group_config = module.GROUPS[category_config["group_code"]]

        rows.append(
            {
                "group_code": group_config["code"],
                "group_name": group_config["name"],
                "category_code": category_config["category_code"],
                "category_name": category_config["category_name"],
                "mapping_code": category_config["mapping_code"],
                "mapping_name": category_config["mapping_name"],
                "detail_code": row["country_code"],
                "detail_name": row["country_name"],
            }
        )

    return rows


COUNTRY_PLAN = SeedPlan(
    group=LevelConfig(model=GuestCountryGroup),
    category=LevelConfig(model=GuestCountryCategory, parent_field="group"),
    mapping=LevelConfig(model=GuestCountryMapping, parent_field="category"),
    detail=LevelConfig(model=GuestCountryDetail, parent_field="mapping"),
    group_key="group_code",
    group_name_key="group_name",
    category_key="category_code",
    category_name_key="category_name",
    category_parent_key="group_code",
    mapping_key="mapping_code",
    mapping_name_key="mapping_name",
    mapping_parent_key="category_code",
    detail_key="detail_code",
    detail_name_key="detail_name",
    detail_parent_getter=lambda row, group_cache, category_cache, mapping_cache: mapping_cache[row["mapping_code"]],
    detail_extra_updates_getter=lambda row: {"is_review_required": False},
)


DEFAULT_SEED_REGISTRY = {
    "booking_source": DomainRegistryItem(
        module_path="apps.settings.mappings.data.booking_source",
        structure_getter=lambda module, **kwargs: module.get_default_booking_source_structure(),
        plan=standard_plan(BookingSourceGroup, BookingSourceCategory, BookingSourceMapping),
    ),
    "company": DomainRegistryItem(
        module_path="apps.settings.mappings.data.company",
        structure_getter=lambda module, **kwargs: module.get_default_company_industry_structure(),
        plan=standard_plan(CompanyGroup, CompanyCategory, CompanyMapping),
    ),
    "competitor": DomainRegistryItem(
        module_path="apps.settings.mappings.data.competitor",
        structure_getter=lambda module, **kwargs: module.get_default_competitor_structure(),
        plan=standard_plan(CompetitorGroup, CompetitorCategory, CompetitorMapping),
    ),
    "country": DomainRegistryItem(
        module_path="apps.settings.mappings.data.country",
        structure_getter=lambda module, **kwargs: build_country_structure(module),
        plan=COUNTRY_PLAN,
    ),
    "day_of_week": DomainRegistryItem(
        module_path="apps.settings.mappings.data.day_of_week",
        structure_getter=lambda module, **kwargs: list(module.DEFAULT_DAY_OF_WEEK_STRUCTURE),
        plan=group_mapping_plan(
            DayOfWeekGroup,
            DayOfWeekMapping,
            mapping_key="day_code",
            mapping_name_key="day_name",
            mapping_parent_key="group_code",
        ),
    ),
    "loyalty": DomainRegistryItem(
        module_path="apps.settings.mappings.data.loyalty",
        structure_getter=lambda module, **kwargs: module.get_default_loyalty_structure(),
        plan=standard_plan(LoyaltyGroup, LoyaltyCategory, LoyaltyMapping),
    ),
    "origin": DomainRegistryItem(
        module_path="apps.settings.mappings.data.origin",
        structure_getter=lambda module, **kwargs: module.get_default_origin_structure(),
        plan=standard_plan(OriginGroup, OriginCategory, OriginMapping),
    ),
    "package": DomainRegistryItem(
        module_path="apps.settings.mappings.data.package",
        structure_getter=lambda module, **kwargs: module.get_default_package_structure(),
        plan=standard_plan(PackageGroup, PackageCategory, PackageMapping),
    ),
    "room_type": DomainRegistryItem(
        module_path="apps.settings.mappings.data.room_type",
        structure_getter=lambda module, **kwargs: module.get_default_room_type_structure(
            include_apartments=kwargs.get("include_apartments", False)
        ),
        plan=standard_plan(RoomTypeGroup, RoomTypeCategory, RoomTypeMapping),
    ),
    "segment": DomainRegistryItem(
        module_path="apps.settings.mappings.data.segment",
        structure_getter=lambda module, **kwargs: list(module.DEFAULT_SEGMENT_STRUCTURE),
        plan=SeedPlan(
            group=LevelConfig(model=SegmentGroup),
            category=LevelConfig(model=SegmentCategory, parent_field="group"),
            mapping=LevelConfig(model=SegmentMapping, parent_field="category"),
            group_key="group_code",
            group_name_key="group_name",
            category_key="category_code",
            category_name_key="category_name",
            category_parent_key="group_code",
            mapping_key="segment_code",
            mapping_name_key="segment_name",
            mapping_parent_key="category_code",
        ),
    ),
    "travel_agency": DomainRegistryItem(
        module_path="apps.settings.mappings.data.travel_agency",
        structure_getter=lambda module, **kwargs: module.get_default_travel_agency_structure(),
        plan=standard_plan(TravelAgentGroup, TravelAgentCategory, TravelAgentMapping),
    ),
}


def get_seed_registry_item(domain_key: str) -> DomainRegistryItem:
    try:
        return DEFAULT_SEED_REGISTRY[domain_key]
    except KeyError as exc:
        raise KeyError(
            f"Unknown seed domain '{domain_key}'. "
            f"Available domains: {', '.join(sorted(DEFAULT_SEED_REGISTRY.keys()))}"
        ) from exc


def load_seed_module(domain_key: str):
    item = get_seed_registry_item(domain_key)
    return import_module(item.module_path)