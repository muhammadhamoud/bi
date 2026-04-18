from django.core.management.base import BaseCommand

from apps.dataops.files.models import SourceSystem
from apps.properties.core.models import Property
from apps.settings.mappings.models import (
    RoomTypeGroup,
    RoomTypeMapping,
    PackageGroup,
    PackageMapping,
    RateCodeGroup,
    RateCodeMapping,
    TravelAgentGroup,
    TravelAgentMapping,
    GuestCountryGroup,
    GuestCountryMapping,
    CompanyGroup,
    CompanyMapping,
    DayOfWeekGroup,
    DayOfWeekMapping,
    BookingSourceGroup,
    BookingSourceMapping,
    OriginGroup,
    OriginMapping,
    CompetitorGroup,
    CompetitorMapping,
    LoyaltyGroup,
    LoyaltyMapping,
)


class Command(BaseCommand):
    help = 'Seed demo mapping data across all non-segmentation mapping domains.'

    def handle(self, *args, **options):
        property_obj = Property.objects.filter(is_active=True).first()
        if not property_obj:
            self.stdout.write(self.style.WARNING('No properties found. Run seed_properties first.'))
            return
        source_system = SourceSystem.objects.filter(is_active=True).first()
        room_types_group, _ = RoomTypeGroup.objects.get_or_create(
            property=property_obj,
            code='ROOM-GRP',
            defaults={'name': 'Room Type Core', 'description': 'Define room categories and pricing relationships to keep inventory structured and easy to analyze.'}
        )
        RoomTypeMapping.objects.get_or_create(
            property=property_obj,
            group=room_types_group,
            source_code='ROOM-SRC-1',
            defaults={
                "source_system": source_system,
                'source_label': 'Room Type source example',
                'mapped_code': 'ROOM-MAP-1',
                'mapped_label': 'Room Type mapped example',
                'notes': 'Demo mapped record',
            },
        )
        RoomTypeMapping.objects.get_or_create(
            property=property_obj,
            group=room_types_group,
            source_code='ROOM-SRC-2',
            defaults={
                "source_system": source_system,
                'source_label': 'Room Type needs review',
                'mapped_code': '',
                'mapped_label': '',
                'is_review_required': True,
                'notes': 'Demo unmapped record',
            },
        )
        packages_group, _ = PackageGroup.objects.get_or_create(
            property=property_obj,
            code='PACK-GRP',
            defaults={'name': 'Package Core', 'description': 'Organize packages into clear groups so you can measure which offers drive the most bookings and revenue.'}
        )
        PackageMapping.objects.get_or_create(
            property=property_obj,
            group=packages_group,
            source_code='PACK-SRC-1',
            defaults={
                "source_system": source_system,
                'source_label': 'Package source example',
                'mapped_code': 'PACK-MAP-1',
                'mapped_label': 'Package mapped example',
                'notes': 'Demo mapped record',
            },
        )
        PackageMapping.objects.get_or_create(
            property=property_obj,
            group=packages_group,
            source_code='PACK-SRC-2',
            defaults={
                "source_system": source_system,
                'source_label': 'Package needs review',
                'mapped_code': '',
                'mapped_label': '',
                'is_review_required': True,
                'notes': 'Demo unmapped record',
            },
        )
        rate_codes_group, _ = RateCodeGroup.objects.get_or_create(
            property=property_obj,
            code='RATE-GRP',
            defaults={'name': 'Rate Code Core', 'description': 'Structure rate codes into meaningful groups to track performance and identify the most effective pricing strategies.'}
        )
        RateCodeMapping.objects.get_or_create(
            property=property_obj,
            group=rate_codes_group,
            source_code='RATE-SRC-1',
            defaults={
                "source_system": source_system,
                'source_label': 'Rate Code source example',
                'mapped_code': 'RATE-MAP-1',
                'mapped_label': 'Rate Code mapped example',
                'notes': 'Demo mapped record',
            },
        )
        RateCodeMapping.objects.get_or_create(
            property=property_obj,
            group=rate_codes_group,
            source_code='RATE-SRC-2',
            defaults={
                "source_system": source_system,
                'source_label': 'Rate Code needs review',
                'mapped_code': '',
                'mapped_label': '',
                'is_review_required': True,
                'notes': 'Demo unmapped record',
            },
        )
        travel_agents_group, _ = TravelAgentGroup.objects.get_or_create(
            property=property_obj,
            code='TRAV-GRP',
            defaults={'name': 'Travel Agent Core', 'description': 'Organize travel agents to evaluate performance, strengthen partnerships, and uncover new business opportunities.'}
        )
        TravelAgentMapping.objects.get_or_create(
            property=property_obj,
            group=travel_agents_group,
            source_code='TRAV-SRC-1',
            defaults={
                "source_system": source_system,
                'source_label': 'Travel Agent source example',
                'mapped_code': 'TRAV-MAP-1',
                'mapped_label': 'Travel Agent mapped example',
                'notes': 'Demo mapped record',
            },
        )
        TravelAgentMapping.objects.get_or_create(
            property=property_obj,
            group=travel_agents_group,
            source_code='TRAV-SRC-2',
            defaults={
                "source_system": source_system,
                'source_label': 'Travel Agent needs review',
                'mapped_code': '',
                'mapped_label': '',
                'is_review_required': True,
                'notes': 'Demo unmapped record',
            },
        )
        guest_countries_group, _ = GuestCountryGroup.objects.get_or_create(
            property=property_obj,
            code='GUES-GRP',
            defaults={'name': 'Guest Country Core', 'description': 'See where guests are coming from so marketing efforts can be refined and the right audiences can be targeted.'}
        )
        GuestCountryMapping.objects.get_or_create(
            property=property_obj,
            group=guest_countries_group,
            source_code='GUES-SRC-1',
            defaults={
                "source_system": source_system,
                'source_label': 'Guest Country source example',
                'mapped_code': 'GUES-MAP-1',
                'mapped_label': 'Guest Country mapped example',
                'notes': 'Demo mapped record',
            },
        )
        GuestCountryMapping.objects.get_or_create(
            property=property_obj,
            group=guest_countries_group,
            source_code='GUES-SRC-2',
            defaults={
                "source_system": source_system,
                'source_label': 'Guest Country needs review',
                'mapped_code': '',
                'mapped_label': '',
                'is_review_required': True,
                'notes': 'Demo unmapped record',
            },
        )
        companies_group, _ = CompanyGroup.objects.get_or_create(
            property=property_obj,
            code='COMP-GRP',
            defaults={'name': 'Company Core', 'description': 'Classify reservations by company to support corporate account management and grow the business segment.'}
        )
        CompanyMapping.objects.get_or_create(
            property=property_obj,
            group=companies_group,
            source_code='COMP-SRC-1',
            defaults={
                "source_system": source_system,
                'source_label': 'Company source example',
                'mapped_code': 'COMP-MAP-1',
                'mapped_label': 'Company mapped example',
                'notes': 'Demo mapped record',
            },
        )
        CompanyMapping.objects.get_or_create(
            property=property_obj,
            group=companies_group,
            source_code='COMP-SRC-2',
            defaults={
                "source_system": source_system,
                'source_label': 'Company needs review',
                'mapped_code': '',
                'mapped_label': '',
                'is_review_required': True,
                'notes': 'Demo unmapped record',
            },
        )
        day_of_week_group, _ = DayOfWeekGroup.objects.get_or_create(
            property=property_obj,
            code='DAYO-GRP',
            defaults={'name': 'Day of Week Core', 'description': 'Create weekday and weekend groupings that match business logic for clearer demand analysis.'}
        )
        DayOfWeekMapping.objects.get_or_create(
            property=property_obj,
            group=day_of_week_group,
            source_code='DAYO-SRC-1',
            defaults={
                "source_system": source_system,
                'source_label': 'Day of Week source example',
                'mapped_code': 'DAYO-MAP-1',
                'mapped_label': 'Day of Week mapped example',
                'notes': 'Demo mapped record',
            },
        )
        DayOfWeekMapping.objects.get_or_create(
            property=property_obj,
            group=day_of_week_group,
            source_code='DAYO-SRC-2',
            defaults={
                "source_system": source_system,
                'source_label': 'Day of Week needs review',
                'mapped_code': '',
                'mapped_label': '',
                'is_review_required': True,
                'notes': 'Demo unmapped record',
            },
        )
        booking_sources_group, _ = BookingSourceGroup.objects.get_or_create(
            property=property_obj,
            code='BOOK-GRP',
            defaults={'name': 'Booking Source Core', 'description': 'Organize booking channels like direct, wholesale, and OTA sources to sharpen distribution insights.'}
        )
        BookingSourceMapping.objects.get_or_create(
            property=property_obj,
            group=booking_sources_group,
            source_code='BOOK-SRC-1',
            defaults={
                "source_system": source_system,
                'source_label': 'Booking Source source example',
                'mapped_code': 'BOOK-MAP-1',
                'mapped_label': 'Booking Source mapped example',
                'notes': 'Demo mapped record',
            },
        )
        BookingSourceMapping.objects.get_or_create(
            property=property_obj,
            group=booking_sources_group,
            source_code='BOOK-SRC-2',
            defaults={
                "source_system": source_system,
                'source_label': 'Booking Source needs review',
                'mapped_code': '',
                'mapped_label': '',
                'is_review_required': True,
                'notes': 'Demo unmapped record',
            },
        )
        origins_group, _ = OriginGroup.objects.get_or_create(
            property=property_obj,
            code='ORIG-GRP',
            defaults={'name': 'Origin Core', 'description': 'Map reservation origins such as websites and channel managers to improve visibility across the booking journey.'}
        )
        OriginMapping.objects.get_or_create(
            property=property_obj,
            group=origins_group,
            source_code='ORIG-SRC-1',
            defaults={
                "source_system": source_system,
                'source_label': 'Origin source example',
                'mapped_code': 'ORIG-MAP-1',
                'mapped_label': 'Origin mapped example',
                'notes': 'Demo mapped record',
            },
        )
        OriginMapping.objects.get_or_create(
            property=property_obj,
            group=origins_group,
            source_code='ORIG-SRC-2',
            defaults={
                "source_system": source_system,
                'source_label': 'Origin needs review',
                'mapped_code': '',
                'mapped_label': '',
                'is_review_required': True,
                'notes': 'Demo unmapped record',
            },
        )
        competitors_group, _ = CompetitorGroup.objects.get_or_create(
            property=property_obj,
            code='COMP-GRP',
            defaults={'name': 'Competitor Core', 'description': 'Set up competitor groups to simplify rate benchmarking and support smarter pricing decisions.'}
        )
        CompetitorMapping.objects.get_or_create(
            property=property_obj,
            group=competitors_group,
            source_code='COMP-SRC-1',
            defaults={
                "source_system": source_system,
                'source_label': 'Competitor source example',
                'mapped_code': 'COMP-MAP-1',
                'mapped_label': 'Competitor mapped example',
                'notes': 'Demo mapped record',
            },
        )
        CompetitorMapping.objects.get_or_create(
            property=property_obj,
            group=competitors_group,
            source_code='COMP-SRC-2',
            defaults={
                "source_system": source_system,
                'source_label': 'Competitor needs review',
                'mapped_code': '',
                'mapped_label': '',
                'is_review_required': True,
                'notes': 'Demo unmapped record',
            },
        )
        loyalties_group, _ = LoyaltyGroup.objects.get_or_create(
            property=property_obj,
            code='LOYA-GRP',
            defaults={'name': 'Loyalty Core', 'description': 'Organize loyalty data into meaningful tiers or groups to better understand member value and engagement.'}
        )
        LoyaltyMapping.objects.get_or_create(
            property=property_obj,
            group=loyalties_group,
            source_code='LOYA-SRC-1',
            defaults={
                "source_system": source_system,
                'source_label': 'Loyalty source example',
                'mapped_code': 'LOYA-MAP-1',
                'mapped_label': 'Loyalty mapped example',
                'notes': 'Demo mapped record',
            },
        )
        LoyaltyMapping.objects.get_or_create(
            property=property_obj,
            group=loyalties_group,
            source_code='LOYA-SRC-2',
            defaults={
                "source_system": source_system,
                'source_label': 'Loyalty needs review',
                'mapped_code': '',
                'mapped_label': '',
                'is_review_required': True,
                'notes': 'Demo unmapped record',
            },
        )
        self.stdout.write(self.style.SUCCESS('Mapping demo data seeded.'))
