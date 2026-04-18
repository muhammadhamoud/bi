from django.core.management.base import BaseCommand

from apps.powerbi.embedded.models import PowerBIReport, PropertyReportGroupSubscription, ReportGroup
from apps.properties.core.models import Property


class Command(BaseCommand):
    help = 'Seed demo Power BI report groups and reports.'

    def handle(self, *args, **options):
        properties = list(Property.objects.filter(is_active=True))
        if not properties:
            self.stdout.write(self.style.WARNING('No properties available. Run seed_properties first.'))
            return

        revenue_group, _ = ReportGroup.objects.get_or_create(
            slug='revenue-reports',
            defaults={
                'name': 'Revenue Reports',
                'description': 'Revenue, ADR, RevPAR, and month-end finance views.',
                'sort_order': 1,
                'icon': 'chart-bar',
            },
        )
        operations_group, _ = ReportGroup.objects.get_or_create(
            slug='operations-reports',
            defaults={
                'name': 'Operations Reports',
                'description': 'Daily operations, arrivals, departures, and service monitoring.',
                'sort_order': 2,
                'icon': 'clipboard',
            },
        )
        for property_obj in properties[:2]:
            PropertyReportGroupSubscription.objects.get_or_create(property=property_obj, report_group=revenue_group)
            PropertyReportGroupSubscription.objects.get_or_create(property=property_obj, report_group=operations_group)

        reports = [
            {
                'report_group': revenue_group,
                'name': 'Monthly Revenue Summary',
                'slug': 'monthly-revenue-summary',
                'description': 'Executive financial summary with trend analysis and property rollups.',
                'powerbi_report_id': '00000000-0000-0000-0000-000000000001',
                'workspace_id': '11111111-1111-1111-1111-111111111111',
                'dataset_id': '22222222-2222-2222-2222-222222222222',
                'embed_url': 'https://app.powerbi.com/reportEmbed?reportId=00000000-0000-0000-0000-000000000001',
                'sort_order': 1,
            },
            {
                'report_group': operations_group,
                'name': 'Daily Operations Monitor',
                'slug': 'daily-operations-monitor',
                'description': 'Operational readiness, occupancy pickup, and service alerts.',
                'powerbi_report_id': '00000000-0000-0000-0000-000000000002',
                'workspace_id': '11111111-1111-1111-1111-111111111111',
                'dataset_id': '22222222-2222-2222-2222-222222222223',
                'embed_url': 'https://app.powerbi.com/reportEmbed?reportId=00000000-0000-0000-0000-000000000002',
                'sort_order': 1,
            },
        ]
        for payload in reports:
            PowerBIReport.objects.get_or_create(slug=payload['slug'], defaults=payload)
        self.stdout.write(self.style.SUCCESS('Power BI demo metadata seeded.'))
