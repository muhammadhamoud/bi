from apps.settings.mappings.models.base import MappingGroupBase, PropertyScopedModel, SourceMappingBase
from apps.settings.mappings.models.segmentations import SegmentMapping, SegmentCategory, SegmentDetail, SegmentGroup
from apps.settings.mappings.models.day_of_week import DayOfWeekGroup, DayOfWeekMapping
from apps.settings.mappings.models.booking_sources import BookingSourceGroup, BookingSourceMapping, BookingSourceCategory, BookingSourceDetail
from apps.settings.mappings.models.room_types import RoomTypeGroup, RoomTypeMapping, RoomTypeCategory, RoomTypeDetail
from apps.settings.mappings.models.packages import PackageGroup, PackageMapping, PackageCategory, PackageDetail
from apps.settings.mappings.models.rate_codes import RateCodeDetail #RateCodeGroup, , RateCodeCategory, RateCodeMapping
from apps.settings.mappings.models.travel_agents import TravelAgentGroup, TravelAgentMapping, TravelAgentCategory, TravelAgentDetail
from apps.settings.mappings.models.guest_countries import GuestCountryGroup, GuestCountryMapping, GuestCountryCategory, GuestCountryDetail
from apps.settings.mappings.models.companies import CompanyGroup, CompanyMapping, CompanyCategory, CompanyDetail
from apps.settings.mappings.models.origins import OriginGroup, OriginMapping, OriginCategory, OriginDetail
from apps.settings.mappings.models.competitors import CompetitorGroup, CompetitorMapping, CompetitorCategory, CompetitorDetail
from apps.settings.mappings.models.loyalties import LoyaltyGroup, LoyaltyMapping, LoyaltyCategory, LoyaltyDetail
