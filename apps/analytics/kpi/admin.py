from django.contrib import admin

from apps.analytics.kpi.models import PropertyDailyMetric


@admin.register(PropertyDailyMetric)
class PropertyDailyMetricAdmin(admin.ModelAdmin):
    list_display = ('property', 'metric_date', 'available_rooms', 'rooms_sold', 'room_revenue', 'total_revenue', 'revenue_goal')
    list_filter = ('property', 'metric_date')
    search_fields = ('property__name', 'property__code')
    date_hierarchy = 'metric_date'
    autocomplete_fields = ('property',)
