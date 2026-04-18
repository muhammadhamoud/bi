from django.contrib import admin

from apps.usermanagement.profiles.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme_preference', 'timezone', 'locale', 'receive_email_notifications', 'receive_product_announcements')
    list_filter = ('theme_preference', 'receive_email_notifications', 'receive_product_announcements')
    search_fields = ('user__email', 'user__display_name', 'user__first_name', 'user__last_name')
    autocomplete_fields = ('user',)
