from django.contrib import admin

from apps.powerbi.embedded.models import PowerBIReport, PropertyReportGroupSubscription, ReportGroup, ReportViewAuditLog


class PowerBIReportInline(admin.TabularInline):
    model = PowerBIReport
    extra = 0
    fields = ('name', 'slug', 'is_active', 'sort_order', 'workspace_id', 'powerbi_report_id')
    show_change_link = True


@admin.register(ReportGroup)
class ReportGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sort_order', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PowerBIReportInline]


@admin.register(PowerBIReport)
class PowerBIReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'report_group', 'slug', 'is_active', 'sort_order', 'last_synced_at')
    list_filter = ('is_active', 'report_group', 'last_synced_at')
    search_fields = ('name', 'slug', 'description', 'workspace_id', 'powerbi_report_id', 'dataset_id')
    autocomplete_fields = ('report_group', 'created_by', 'updated_by')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(PropertyReportGroupSubscription)
class PropertyReportGroupSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('property', 'report_group', 'is_active', 'starts_on', 'ends_on')
    list_filter = ('is_active', 'report_group', 'property')
    search_fields = ('property__name', 'property__code', 'report_group__name')
    autocomplete_fields = ('property', 'report_group')


@admin.register(ReportViewAuditLog)
class ReportViewAuditLogAdmin(admin.ModelAdmin):
    list_display = ('report', 'user', 'property', 'success', 'created_at')
    list_filter = ('success', 'property', 'report')
    search_fields = ('report__name', 'user__email', 'property__name', 'detail')
    autocomplete_fields = ('report', 'user', 'property')
    readonly_fields = ('created_at', 'updated_at')
