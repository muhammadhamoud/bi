from django.contrib import admin

from apps.notifications.announcements.models import Announcement, AnnouncementAcknowledgement


class AnnouncementAcknowledgementInline(admin.TabularInline):
    model = AnnouncementAcknowledgement
    extra = 0
    autocomplete_fields = ('user',)
    readonly_fields = ('read_at', 'dismissed_at', 'created_at', 'updated_at')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'is_active', 'is_published', 'starts_at', 'ends_at', 'created_at')
    list_filter = ('level', 'is_active', 'is_published', 'starts_at', 'ends_at')
    search_fields = ('title', 'body', 'target_roles')
    filter_horizontal = ('properties',)
    autocomplete_fields = ('created_by', 'updated_by')
    inlines = [AnnouncementAcknowledgementInline]


@admin.register(AnnouncementAcknowledgement)
class AnnouncementAcknowledgementAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'user', 'read_at', 'dismissed_at', 'created_at')
    list_filter = ('read_at', 'dismissed_at')
    search_fields = ('announcement__title', 'user__email')
    autocomplete_fields = ('announcement', 'user')
    readonly_fields = ('created_at', 'updated_at')
