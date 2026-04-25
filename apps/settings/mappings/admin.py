from django.contrib import admin

from apps.settings.mappings.models import (
    BookingSourceCategory,
    BookingSourceDetail,
    BookingSourceGroup,
    BookingSourceMapping,
    CompanyCategory,
    CompanyDetail,
    CompanyGroup,
    CompanyMapping,
    CompetitorCategory,
    CompetitorDetail,
    CompetitorGroup,
    CompetitorMapping,
    DayOfWeekGroup,
    DayOfWeekMapping,
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
    RateCodeDetail,
    # RateCodeCategory,
    # RateCodeGroup,
    # RateCodeMapping,
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
)


class PropertyScopedAdmin(admin.ModelAdmin):
    autocomplete_fields = ('property', 'created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = ('property', 'is_active')


class MappingGroupAdmin(PropertyScopedAdmin):
    list_display = ('name', 'code', 'property', 'sort_order', 'is_active')
    search_fields = ('name', 'code', 'description', 'property__name', 'property__code')
    list_select_related = ('property',)


class MappingCategoryAdmin(PropertyScopedAdmin):
    autocomplete_fields = PropertyScopedAdmin.autocomplete_fields + ('group',)
    list_display = ('name', 'code', 'property', 'group', 'sort_order', 'is_active')
    search_fields = (
        'name',
        'code',
        'description',
        'property__name',
        'property__code',
        'group__name',
        'group__code',
    )
    list_filter = PropertyScopedAdmin.list_filter + ('group',)
    list_select_related = ('property', 'group')


class HierarchyMappingAdmin(PropertyScopedAdmin):
    autocomplete_fields = PropertyScopedAdmin.autocomplete_fields + ('category',)
    list_display = ('name', 'code', 'property', 'category', 'sort_order', 'is_active')
    search_fields = (
        'name',
        'code',
        'description',
        'property__name',
        'property__code',
        'category__name',
        'category__code',
        'category__group__name',
        'category__group__code',
    )
    list_filter = PropertyScopedAdmin.list_filter + ('category',)
    list_select_related = ('property', 'category', 'category__group')


class HierarchyDetailAdmin(PropertyScopedAdmin):
    autocomplete_fields = PropertyScopedAdmin.autocomplete_fields + ('source_system', 'mapping')
    list_display = ('code', 'name', 'property', 'mapping', 'is_active', 'is_review_required')
    search_fields = (
        'code',
        'name',
        'description',
        'property__name',
        'property__code',
        'mapping__name',
        'mapping__code',
        'mapping__category__name',
        'mapping__category__code',
        'mapping__category__group__name',
        'mapping__category__group__code',
    )
    list_filter = PropertyScopedAdmin.list_filter + ('is_review_required', 'source_system', 'mapping')
    list_select_related = ('property', 'source_system', 'mapping', 'mapping__category', 'mapping__category__group')



def register_hierarchy_admin(group_model, category_model, mapping_model, detail_model):
    admin.site.register(group_model, MappingGroupAdmin)
    admin.site.register(category_model, MappingCategoryAdmin)
    admin.site.register(mapping_model, HierarchyMappingAdmin)
    admin.site.register(detail_model, HierarchyDetailAdmin)


register_hierarchy_admin(SegmentGroup, SegmentCategory, SegmentMapping, SegmentDetail)
register_hierarchy_admin(RoomTypeGroup, RoomTypeCategory, RoomTypeMapping, RoomTypeDetail)
register_hierarchy_admin(CompanyGroup, CompanyCategory, CompanyMapping, CompanyDetail)
register_hierarchy_admin(CompetitorGroup, CompetitorCategory, CompetitorMapping, CompetitorDetail)
register_hierarchy_admin(GuestCountryGroup, GuestCountryCategory, GuestCountryMapping, GuestCountryDetail)
register_hierarchy_admin(LoyaltyGroup, LoyaltyCategory, LoyaltyMapping, LoyaltyDetail)
register_hierarchy_admin(OriginGroup, OriginCategory, OriginMapping, OriginDetail)
register_hierarchy_admin(PackageGroup, PackageCategory, PackageMapping, PackageDetail)
register_hierarchy_admin(TravelAgentGroup, TravelAgentCategory, TravelAgentMapping, TravelAgentDetail)
register_hierarchy_admin(BookingSourceGroup, BookingSourceCategory, BookingSourceMapping, BookingSourceDetail)
# register_hierarchy_admin(RateCodeGroup, RateCodeCategory, RateCodeMapping, RateCodeDetail)
# register_hierarchy_admin(DayOfWeekGroup, DayOfWeekMapping)


# @admin.register(SegmentDetail)
# class SegmentDetailAdmin(HierarchyDetailAdmin):
#     search_fields = HierarchyDetailAdmin.search_fields + ('notes',)


class SimpleMappingAdmin(PropertyScopedAdmin):
    autocomplete_fields = PropertyScopedAdmin.autocomplete_fields + ('group',)
    list_display = ('name', 'code', 'property', 'group', 'sort_order', 'is_active')
    search_fields = (
        'name',
        'code',
        'description',
        'property__name',
        'property__code',
        'group__name',
        'group__code',
    )
    list_filter = PropertyScopedAdmin.list_filter + ('group',)
    list_select_related = ('property', 'group')

def register_simple_admin(group_model, mapping_model):
    admin.site.register(group_model, MappingGroupAdmin)
    admin.site.register(mapping_model, SimpleMappingAdmin)


register_simple_admin(DayOfWeekGroup, DayOfWeekMapping)




class RateCodeMappingAdmin(PropertyScopedAdmin):
    autocomplete_fields = PropertyScopedAdmin.autocomplete_fields + ('category',)
    list_display = ('name', 'code', 'property', 'category', 'group', 'sort_order', 'is_active')
    search_fields = (
        'name',
        'code',
        'description',
        'property__name',
        'property__code',
        'category__name',
        'category__code',
    )
    list_filter = PropertyScopedAdmin.list_filter + ('category',)
    list_select_related = (
        'property',
        'category',
        'category__mapping',
        'category__mapping__category',
        'category__mapping__category__group',
    )


class RateCodeDetailAdmin(HierarchyDetailAdmin):
    autocomplete_fields = PropertyScopedAdmin.autocomplete_fields + ('mapping', 'origin', 'source_system')
    list_display = (
        'name',
        'code',
        'property',
        'mapping',
        'category',
        'group',
        'origin',
        'source_system',
        'sort_order',
        'is_active',
    )
    search_fields = (
        'name',
        'code',
        'description',
        'notes',
        'property__name',
        'property__code',
        'mapping__name',
        'mapping__code',
        'mapping__segment__name',
        'mapping__segment__code',
        'origin__name',
        'origin__code',
        'source_system__name',
        'source_system__code',
    )
    list_filter = PropertyScopedAdmin.list_filter + (
        'mapping',
        'origin',
        'source_system',
    )
    list_select_related = (
        'property',
        'mapping',
        'mapping__segment',
        'mapping__segment__mapping',
        'mapping__segment__mapping__category',
        'mapping__segment__mapping__category__group',
        'origin',
        'source_system',
    )


# admin.site.register(RateCodeMapping, RateCodeMappingAdmin)
admin.site.register(RateCodeDetail, RateCodeDetailAdmin)