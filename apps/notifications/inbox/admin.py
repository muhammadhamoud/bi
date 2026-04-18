from django.contrib import admin

from apps.notifications.inbox.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'level', 'read_at', 'created_at')
    list_filter = ('level', 'read_at', 'created_at')
    search_fields = ('title', 'message', 'recipient__email')
    autocomplete_fields = ('recipient',)
    readonly_fields = ('created_at', 'updated_at')
