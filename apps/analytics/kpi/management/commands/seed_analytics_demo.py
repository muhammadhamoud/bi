from datetime import timedelta
from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.analytics.kpi.models import PropertyDailyMetric
from apps.properties.core.models import Property


class Command(BaseCommand):
    help = 'Seed 60 days of demo KPI metrics per property.'

    def handle(self, *args, **options):
        random.seed(42)
        today = timezone.localdate()
        for property_obj in Property.objects.filter(is_active=True):
            base_rooms = property_obj.total_rooms or 120
            for offset in range(60):
                metric_date = today - timedelta(days=offset)
                available_rooms = base_rooms if base_rooms else 80
                rooms_sold = max(0, min(available_rooms, int(available_rooms * random.uniform(0.58, 0.91))))
                room_revenue = Decimal(rooms_sold * random.uniform(350, 790)).quantize(Decimal('0.01'))
                total_revenue = (room_revenue * Decimal(random.uniform(1.15, 1.42))).quantize(Decimal('0.01'))
                revenue_goal = Decimal(available_rooms * random.uniform(420, 650)).quantize(Decimal('0.01'))
                occupancy_goal = Decimal(random.uniform(72, 88)).quantize(Decimal('0.01'))
                PropertyDailyMetric.objects.update_or_create(
                    property=property_obj,
                    metric_date=metric_date,
                    defaults={
                        'available_rooms': available_rooms,
                        'rooms_sold': rooms_sold,
                        'room_revenue': room_revenue,
                        'total_revenue': total_revenue,
                        'revenue_goal': revenue_goal,
                        'occupancy_goal': occupancy_goal,
                    },
                )
        self.stdout.write(self.style.SUCCESS('Analytics demo metrics seeded.'))
