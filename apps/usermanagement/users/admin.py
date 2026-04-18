from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.usermanagement.users.models import User, UserPropertyAccess


class UserPropertyAccessInline(admin.TabularInline):
    model = UserPropertyAccess
    extra = 0
    fk_name = "user"   # use the FK field that points to the parent User
    autocomplete_fields = ('property', 'assigned_by')
    fields = ('property', 'is_primary', 'is_active', 'assigned_by', 'notes')


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ('email', 'username', 'display_name', 'job_title', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('email', 'username', 'display_name', 'first_name', 'last_name')
    ordering = ('email',)
    inlines = [UserPropertyAccessInline]
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('display_name', 'first_name', 'last_name', 'phone_number', 'job_title')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Preferences', {'fields': ('preferences',)}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'username', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
            },
        ),
    )


@admin.register(UserPropertyAccess)
class UserPropertyAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'is_primary', 'is_active', 'assigned_by', 'updated_at')
    list_filter = ('is_primary', 'is_active', 'property')
    search_fields = ('user__email', 'user__display_name', 'property__name', 'property__code')
    autocomplete_fields = ('user', 'property', 'assigned_by')
