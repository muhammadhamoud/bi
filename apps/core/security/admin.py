from django.contrib import admin

from apps.core.security.models import SecurityEvent


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('category', 'event_type', 'severity', 'user', 'property', 'created_at')
    list_filter = ('severity', 'category', 'event_type', 'property')
    search_fields = ('category', 'event_type', 'object_repr', 'user__email', 'property__name')
    autocomplete_fields = ('user', 'property')
    readonly_fields = ('created_at', 'updated_at')
