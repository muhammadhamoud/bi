from django.db import models

from apps.core.common.models import TimeStampedModel


class PropertyDailyMetric(TimeStampedModel):
    property = models.ForeignKey('propertycore.Property', on_delete=models.CASCADE, related_name='daily_metrics')
    metric_date = models.DateField(db_index=True)
    available_rooms = models.PositiveIntegerField(default=0)
    rooms_sold = models.PositiveIntegerField(default=0)
    room_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    revenue_goal = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    occupancy_goal = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    class Meta:
        db_table = 'analytics_property_daily_metrics'
        unique_together = ('property', 'metric_date')
        ordering = ['property__name', '-metric_date']
        verbose_name = 'Property daily metric'
        verbose_name_plural = 'Property daily metrics'

    def __str__(self):
        return f'{self.property.name} / {self.metric_date}'
