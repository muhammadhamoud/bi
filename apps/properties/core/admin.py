from django.contrib import admin

from apps.properties.core.models import Organization, Property


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'business_type', 'headquarters_city', 'headquarters_country', 'is_active')
    list_filter = ('business_type', 'is_active')
    search_fields = ('name', 'code', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'organization', 'property_type', 'city', 'country', 'currency', 'is_active')
    list_filter = ('property_type', 'currency', 'country', 'is_active', 'organization')
    search_fields = ('name', 'code', 'slug', 'city', 'country', 'organization__name')
    autocomplete_fields = ('organization',)
    prepopulated_fields = {'slug': ('name',)}
