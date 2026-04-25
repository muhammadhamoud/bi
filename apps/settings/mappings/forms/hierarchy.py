from apps.settings.mappings.forms.common import (
    BaseCategoryForm,
    BaseGroupForm,
    BaseHierarchyDetailForm,
    BaseHierarchyMappingForm,
)
from apps.settings.mappings.models import (
    CompanyCategory,
    CompanyDetail,
    CompanyGroup,
    CompanyMapping,
    CompetitorCategory,
    CompetitorDetail,
    CompetitorGroup,
    CompetitorMapping,
    GuestCountryCategory,
    GuestCountryDetail,
    GuestCountryGroup,
    GuestCountryMapping,
    LoyaltyCategory,
    LoyaltyDetail,
    LoyaltyGroup,
    LoyaltyMapping,
    OriginCategory,
    OriginDetail,
    OriginGroup,
    OriginMapping,
    PackageCategory,
    PackageDetail,
    PackageGroup,
    PackageMapping,
    # RateCodeCategory,
    # RateCodeGroup,
    # RateCodeMapping,
    RateCodeDetail,
    RoomTypeCategory,
    RoomTypeDetail,
    RoomTypeGroup,
    RoomTypeMapping,
    SegmentMapping,
    SegmentCategory,
    SegmentDetail,
    SegmentGroup,
    TravelAgentCategory,
    TravelAgentDetail,
    TravelAgentGroup,
    TravelAgentMapping,
    BookingSourceCategory,
    BookingSourceDetail,
    BookingSourceGroup,
    BookingSourceMapping,
    DayOfWeekGroup, DayOfWeekMapping,
)



class BookingSourceGroupForm(BaseGroupForm):
    class Meta:
        model = BookingSourceGroup
        fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


class BookingSourceCategoryForm(BaseCategoryForm):
    relation_model = BookingSourceGroup
    relation_error_message = 'Selected group must belong to the selected property.'

    class Meta:
        model = BookingSourceCategory
        fields = ['property', 'group', 'code', 'name', 'description', 'sort_order', 'is_active']


class BookingSourceMappingForm(BaseHierarchyMappingForm):
    relation_model = BookingSourceCategory
    relation_error_message = 'Selected category must belong to the selected property.'

    class Meta:
        model = BookingSourceMapping
        fields = ['property', 'category', 'code', 'name', 'description', 'sort_order', 'is_active']


class BookingSourceDetailForm(BaseHierarchyDetailForm):
    relation_model = BookingSourceMapping
    relation_error_message = 'Selected mapping must belong to the selected property.'

    class Meta:
        model = BookingSourceDetail
        fields = [
            'property', 'mapping', 'source_system', 'code', 'name', 'description',
            'notes', 'is_review_required', 'effective_from', 'effective_to',
            'sort_order', 'is_active',
        ]


class SegmentGroupForm(BaseGroupForm):
    class Meta:
        model = SegmentGroup
        fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


class SegmentCategoryForm(BaseCategoryForm):
    relation_model = SegmentGroup
    relation_error_message = 'Selected group must belong to the selected property.'

    class Meta:
        model = SegmentCategory
        fields = ['property', 'group', 'code', 'name', 'description', 'sort_order', 'is_active']


class SegmentForm(BaseHierarchyMappingForm):
    relation_model = SegmentCategory
    relation_error_message = 'Selected category must belong to the selected property.'

    class Meta:
        model = SegmentMapping
        fields = ['property', 'category', 'code', 'name', 'description', 'sort_order', 'is_active']


class SegmentDetailForm(BaseHierarchyDetailForm):
    relation_model = SegmentMapping
    relation_error_message = 'Selected mapping must belong to the selected property.'

    class Meta:
        model = SegmentDetail
        fields = [
            'property', 'mapping', 'code', 'name', 'description',
            'notes', 'effective_from', 'effective_to', 'sort_order',
            'source_system', 'is_active', 'is_review_required',
        ]

class RoomTypeGroupForm(BaseGroupForm):
    class Meta:
        model = RoomTypeGroup
        fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


class RoomTypeCategoryForm(BaseCategoryForm):
    relation_model = RoomTypeGroup
    relation_error_message = 'Selected group must belong to the selected property.'

    class Meta:
        model = RoomTypeCategory
        fields = ['property', 'group', 'code', 'name', 'description', 'sort_order', 'is_active']


class RoomTypeMappingForm(BaseHierarchyMappingForm):
    relation_model = RoomTypeCategory
    relation_error_message = 'Selected category must belong to the selected property.'

    class Meta:
        model = RoomTypeMapping
        fields = ['property', 'category', 'code', 'name', 'description', 'sort_order', 'is_active']


class RoomTypeDetailForm(BaseHierarchyDetailForm):
    relation_model = RoomTypeMapping
    relation_error_message = 'Selected mapping must belong to the selected property.'

    class Meta:
        model = RoomTypeDetail
        fields = [
            'property', 'mapping', 'source_system', 'code', 'name', 'description',
            'notes', 'is_review_required', 'effective_from', 'effective_to',
            'sort_order', 'is_active', 'room_class', 'number_of_rooms', 'room_category'
        ]

class CompanyGroupForm(BaseGroupForm):
    class Meta:
        model = CompanyGroup
        fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


class CompanyCategoryForm(BaseCategoryForm):
    relation_model = CompanyGroup
    relation_error_message = 'Selected group must belong to the selected property.'

    class Meta:
        model = CompanyCategory
        fields = ['property', 'group', 'code', 'name', 'description', 'sort_order', 'is_active']


class CompanyMappingForm(BaseHierarchyMappingForm):
    relation_model = CompanyCategory
    relation_error_message = 'Selected category must belong to the selected property.'

    class Meta:
        model = CompanyMapping
        fields = ['property', 'category', 'code', 'name', 'description', 'sort_order', 'is_active']


class CompanyDetailForm(BaseHierarchyDetailForm):
    relation_model = CompanyMapping
    relation_error_message = 'Selected mapping must belong to the selected property.'

    class Meta:
        model = CompanyDetail
        fields = [
            'property', 'mapping', 'source_system', 'code', 'name', 'description',
            'notes', 'is_review_required', 'effective_from', 'effective_to',
            'sort_order', 'is_active',
        ]

class CompetitorGroupForm(BaseGroupForm):
    class Meta:
        model = CompetitorGroup
        fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


class CompetitorCategoryForm(BaseCategoryForm):
    relation_model = CompetitorGroup
    relation_error_message = 'Selected group must belong to the selected property.'

    class Meta:
        model = CompetitorCategory
        fields = ['property', 'group', 'code', 'name', 'description', 'sort_order', 'is_active']


class CompetitorMappingForm(BaseHierarchyMappingForm):
    relation_model = CompetitorCategory
    relation_error_message = 'Selected category must belong to the selected property.'

    class Meta:
        model = CompetitorMapping
        fields = ['property', 'category', 'code', 'name', 'description', 'sort_order', 'is_active']


class CompetitorDetailForm(BaseHierarchyDetailForm):
    relation_model = CompetitorMapping
    relation_error_message = 'Selected mapping must belong to the selected property.'

    class Meta:
        model = CompetitorDetail
        fields = [
            'property', 'mapping', 'source_system', 'code', 'name', 'description',
            'notes', 'is_review_required', 'effective_from', 'effective_to',
            'sort_order', 'is_active',
        ]

class GuestCountryGroupForm(BaseGroupForm):
    class Meta:
        model = GuestCountryGroup
        fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


class GuestCountryCategoryForm(BaseCategoryForm):
    relation_model = GuestCountryGroup
    relation_error_message = 'Selected group must belong to the selected property.'

    class Meta:
        model = GuestCountryCategory
        fields = ['property', 'group', 'code', 'name', 'description', 'sort_order', 'is_active']


class GuestCountryMappingForm(BaseHierarchyMappingForm):
    relation_model = GuestCountryCategory
    relation_error_message = 'Selected category must belong to the selected property.'

    class Meta:
        model = GuestCountryMapping
        fields = ['property', 'category', 'code', 'name', 'description', 'sort_order', 'is_active']


class GuestCountryDetailForm(BaseHierarchyDetailForm):
    relation_model = GuestCountryMapping
    relation_error_message = 'Selected mapping must belong to the selected property.'

    class Meta:
        model = GuestCountryDetail
        fields = [
            'property', 'mapping', 'source_system', 'code', 'name', 'description',
            'notes', 'is_review_required', 'effective_from', 'effective_to',
            'sort_order', 'is_active',
        ]


class LoyaltyGroupForm(BaseGroupForm):
    class Meta:
        model = LoyaltyGroup
        fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


class LoyaltyCategoryForm(BaseCategoryForm):
    relation_model = LoyaltyGroup
    relation_error_message = 'Selected group must belong to the selected property.'

    class Meta:
        model = LoyaltyCategory
        fields = ['property', 'group', 'code', 'name', 'description', 'sort_order', 'is_active']


class LoyaltyMappingForm(BaseHierarchyMappingForm):
    relation_model = LoyaltyCategory
    relation_error_message = 'Selected category must belong to the selected property.'

    class Meta:
        model = LoyaltyMapping
        fields = ['property', 'category', 'code', 'name', 'description', 'sort_order', 'is_active']


class LoyaltyDetailForm(BaseHierarchyDetailForm):
    relation_model = LoyaltyMapping
    relation_error_message = 'Selected mapping must belong to the selected property.'

    class Meta:
        model = LoyaltyDetail
        fields = [
            'property', 'mapping', 'source_system', 'code', 'name', 'description',
            'notes', 'is_review_required', 'effective_from', 'effective_to',
            'sort_order', 'is_active',
        ]

class OriginGroupForm(BaseGroupForm):
    class Meta:
        model = OriginGroup
        fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


class OriginCategoryForm(BaseCategoryForm):
    relation_model = OriginGroup
    relation_error_message = 'Selected group must belong to the selected property.'

    class Meta:
        model = OriginCategory
        fields = ['property', 'group', 'code', 'name', 'description', 'sort_order', 'is_active']


class OriginMappingForm(BaseHierarchyMappingForm):
    relation_model = OriginCategory
    relation_error_message = 'Selected category must belong to the selected property.'

    class Meta:
        model = OriginMapping
        fields = ['property', 'category', 'code', 'name', 'description', 'sort_order', 'is_active']


class OriginDetailForm(BaseHierarchyDetailForm):
    relation_model = OriginMapping
    relation_error_message = 'Selected mapping must belong to the selected property.'

    class Meta:
        model = OriginDetail
        fields = [
            'property', 'mapping', 'source_system', 'code', 'name', 'description',
            'notes', 'is_review_required', 'effective_from', 'effective_to',
            'sort_order', 'is_active',
        ]

class PackageGroupForm(BaseGroupForm):
    class Meta:
        model = PackageGroup
        fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


class PackageCategoryForm(BaseCategoryForm):
    relation_model = PackageGroup
    relation_error_message = 'Selected group must belong to the selected property.'

    class Meta:
        model = PackageCategory
        fields = ['property', 'group', 'code', 'name', 'description', 'sort_order', 'is_active']


class PackageMappingForm(BaseHierarchyMappingForm):
    relation_model = PackageCategory
    relation_error_message = 'Selected category must belong to the selected property.'

    class Meta:
        model = PackageMapping
        fields = ['property', 'category', 'code', 'name', 'description', 'sort_order', 'is_active']


class PackageDetailForm(BaseHierarchyDetailForm):
    relation_model = PackageMapping
    relation_error_message = 'Selected mapping must belong to the selected property.'

    class Meta:
        model = PackageDetail
        fields = [
            'property', 'mapping', 'source_system', 'code', 'name', 'description',
            'notes', 'is_review_required', 'effective_from', 'effective_to',
            'sort_order', 'is_active',
        ]

# class RateCodeGroupForm(BaseGroupForm):
#     class Meta:
#         model = RateCodeGroup
#         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


# class RateCodeCategoryForm(BaseCategoryForm):
#     relation_model = RateCodeGroup
#     relation_error_message = 'Selected group must belong to the selected property.'

#     class Meta:
#         model = RateCodeCategory
#         fields = ['property', 'group', 'code', 'name', 'description', 'sort_order', 'is_active']


# class RateCodeMappingForm(BaseHierarchyMappingForm):
#     relation_model = SegmentDetail
#     relation_select_related = (
#         'mapping',
#         'mapping__category',
#         'mapping__category__group',
#     )
#     relation_ordering = (
#         'mapping__category__group__name',
#         'mapping__category__name',
#         'name',
#     )
#     relation_error_message = 'Selected category must belong to the selected property.'

#     class Meta:
#         model = RateCodeMapping
#         fields = [
#             'property',
#             'category',
#             'code',
#             'name',
#             'description',
#             'sort_order',
#             'is_active',
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         queryset = SegmentDetail.objects.select_related(
#             'property',
#             'mapping',
#             'mapping__category',
#             'mapping__category__group',
#         ).filter(is_active=True)

#         property_id = None

#         if self.is_bound:
#             property_id = self.data.get('property') or None
#         elif self.instance and self.instance.pk:
#             property_id = self.instance.property_id
#         elif self.initial.get('property'):
#             property_id = self.initial.get('property')

#         if property_id:
#             queryset = queryset.filter(property_id=property_id)

#         self.fields['category'].queryset = queryset.order_by(
#             'mapping__category__group__name',
#             'mapping__category__name',
#             'name',
#         )


class RateCodeDetailForm(BaseHierarchyDetailForm):
    relation_model = SegmentDetail
    relation_select_related = (
        'mapping',
        'mapping__category',
        'mapping__category__group',
    )
    relation_ordering = (
        'mapping__category__group__name',
        'mapping__category__name',
        'name',
    )
    relation_error_message = 'Selected mapping must belong to the selected property.'

    class Meta:
        model = RateCodeDetail
        fields = [
            'property',
            'mapping',
            'origin',
            'source_system',
            'code',
            'name',
            'description',
            'notes',
            'is_review_required',
            'effective_from',
            'effective_to',
            'sort_order',
            'is_active',
        ]
        
class TravelAgentGroupForm(BaseGroupForm):
    class Meta:
        model = TravelAgentGroup
        fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


class TravelAgentCategoryForm(BaseCategoryForm):
    relation_model = TravelAgentGroup
    relation_error_message = 'Selected group must belong to the selected property.'

    class Meta:
        model = TravelAgentCategory
        fields = ['property', 'group', 'code', 'name', 'description', 'sort_order', 'is_active']


class TravelAgentMappingForm(BaseHierarchyMappingForm):
    relation_model = TravelAgentCategory
    relation_error_message = 'Selected category must belong to the selected property.'

    class Meta:
        model = TravelAgentMapping
        fields = ['property', 'category', 'code', 'name', 'description', 'sort_order', 'is_active']


class TravelAgentDetailForm(BaseHierarchyDetailForm):
    relation_model = TravelAgentMapping
    relation_error_message = 'Selected mapping must belong to the selected property.'

    class Meta:
        model = TravelAgentDetail
        fields = [
            'property', 'mapping', 'source_system', 'code', 'name', 'description',
            'notes', 'is_review_required', 'effective_from', 'effective_to',
            'sort_order', 'is_active',
        ]


class DayOfWeekGroupForm(BaseGroupForm):
    class Meta:
        model = DayOfWeekGroup
        fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


class DayOfWeekMappingForm(BaseCategoryForm):
    relation_field_name = 'group'
    relation_model = DayOfWeekGroup
    relation_ordering = ('name',)
    relation_error_message = 'Selected group must belong to the selected property.'

    class Meta:
        model = DayOfWeekMapping
        fields = [
            'property', 'group', 'source_system', 'code', 'name', 'description',
            'notes', 'is_review_required', 'effective_from', 'effective_to',
            'sort_order', 'is_active'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_property_scoped_relation_field()

    def clean_group(self):
        return self.validate_property_scoped_relation('group', self.relation_error_message)


