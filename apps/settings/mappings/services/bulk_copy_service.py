from dataclasses import dataclass, field
from typing import Dict, List

from apps.properties.core.models import Property
from apps.settings.mappings.services.copy_service import MappingCopyService


@dataclass
class DomainCopyResult:
    domain_key: str
    groups_created: int = 0
    groups_updated: int = 0
    groups_skipped: int = 0
    categories_created: int = 0
    categories_updated: int = 0
    categories_skipped: int = 0
    mappings_created: int = 0
    mappings_updated: int = 0
    mappings_skipped: int = 0
    details_created: int = 0
    details_updated: int = 0
    details_skipped: int = 0


@dataclass
class BulkCopyResult:
    results: List[DomainCopyResult] = field(default_factory=list)


class BulkMappingCopyService:
    def __init__(
        self,
        *,
        source_property: Property,
        target_property: Property,
        domain_keys: list[str],
        copy_groups: bool = True,
        copy_categories: bool = True,
        copy_mappings: bool = True,
        copy_details: bool = False,
        mode: str = "skip",
    ):
        self.source_property = source_property
        self.target_property = target_property
        self.domain_keys = domain_keys
        self.copy_groups = copy_groups
        self.copy_categories = copy_categories
        self.copy_mappings = copy_mappings
        self.copy_details = copy_details
        self.mode = mode

    def execute(self):
        bulk_result = BulkCopyResult()

        for domain_key in self.domain_keys:
            stats = MappingCopyService(
                domain_key=domain_key,
                source_property=self.source_property,
                target_property=self.target_property,
                copy_groups=self.copy_groups,
                copy_categories=self.copy_categories,
                copy_mappings=self.copy_mappings,
                copy_details=self.copy_details,
                mode=self.mode,
            ).execute()

            bulk_result.results.append(
                DomainCopyResult(
                    domain_key=domain_key,
                    groups_created=stats.groups_created,
                    groups_updated=stats.groups_updated,
                    groups_skipped=stats.groups_skipped,
                    categories_created=stats.categories_created,
                    categories_updated=stats.categories_updated,
                    categories_skipped=stats.categories_skipped,
                    mappings_created=stats.mappings_created,
                    mappings_updated=stats.mappings_updated,
                    mappings_skipped=stats.mappings_skipped,
                    details_created=stats.details_created,
                    details_updated=stats.details_updated,
                    details_skipped=stats.details_skipped,
                )
            )

        return bulk_result