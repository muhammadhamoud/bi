from django.core.management.base import BaseCommand

from apps.powerbi.embedded.models import (
    PowerBIReport,
    PropertyReportGroupSubscription,
    ReportGroup,
)
from apps.properties.core.models import Property


REPORT_GROUPS = [
    {
        "name": "Topline Financials",
        "slug": "topline-financials",
        "description": "Executive summary reporting for topline revenue, budget performance, and profitability.",
        "icon": "fa-chart-line",
        "color": "emerald",
        "sort_order": 1,
    },
    {
        "name": "Distribution",
        "slug": "distribution",
        "description": "Channel contribution, booking sources, and distribution cost reporting.",
        "icon": "fa-network-wired",
        "color": "blue",
        "sort_order": 2,
    },
    {
        "name": "Segmentation",
        "slug": "segmentation",
        "description": "Business mix reporting by market segment, source, and rate category.",
        "icon": "fa-layer-group",
        "color": "violet",
        "sort_order": 3,
    },
    {
        "name": "Forecasting & Budget",
        "slug": "forecasting-budget",
        "description": "Forward-looking revenue, occupancy, ADR, and budget tracking reports.",
        "icon": "fa-calendar-day",
        "color": "amber",
        "sort_order": 4,
    },
    {
        "name": "Account Management",
        "slug": "account-management",
        "description": "Production and performance reporting for accounts, agencies, and corporate clients.",
        "icon": "fa-briefcase",
        "color": "indigo",
        "sort_order": 5,
    },
    {
        "name": "Booking Activity & Patterns",
        "slug": "booking-activity-patterns",
        "description": "Pickup, pace, booking behavior, lead time, and stay pattern reports.",
        "icon": "fa-calendar-check",
        "color": "cyan",
        "sort_order": 6,
    },
    {
        "name": "Cancellation & No-Show",
        "slug": "cancellation-no-show",
        "description": "Reports focused on cancellations, no-shows, wash, and refund behaviors.",
        "icon": "fa-ban",
        "color": "rose",
        "sort_order": 7,
    },
    {
        "name": "Pricing & Inventory",
        "slug": "pricing-inventory",
        "description": "Rate strategy, inventory controls, restrictions, and room availability reports.",
        "icon": "fa-tags",
        "color": "orange",
        "sort_order": 8,
    },
    {
        "name": "Demand, Supply & Market Share",
        "slug": "demand-supply-market-share",
        "description": "Demand trends, supply constraints, and market benchmark reporting.",
        "icon": "fa-chart-area",
        "color": "teal",
        "sort_order": 9,
    },
    {
        "name": "Geo Source & Market Mix",
        "slug": "geo-source-market-mix",
        "description": "Source market and geographic contribution reporting.",
        "icon": "fa-globe",
        "color": "sky",
        "sort_order": 10,
    },
]


REPORTS = [
    {
        "report_group_slug": "topline-financials",
        "name": "Executive Revenue Summary",
        "slug": "executive-revenue-summary",
        "description": "High-level summary of total revenue, rooms revenue, F&B revenue, and other departments.",
        "sort_order": 1,
        "powerbi_report_id": "PBI-EXEC-REV-SUMMARY",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-EXEC-REV-SUMMARY",
    },
    {
        "report_group_slug": "topline-financials",
        "name": "Actual vs Budget",
        "slug": "actual-vs-budget",
        "description": "Comparison of actual performance against budget by period and property.",
        "sort_order": 2,
        "powerbi_report_id": "PBI-ACTUAL-VS-BUDGET",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-ACTUAL-VS-BUDGET",
    },
    {
        "report_group_slug": "topline-financials",
        "name": "YTD Performance",
        "slug": "ytd-performance",
        "description": "Year-to-date performance including revenue, GOP, NOP, and key KPIs.",
        "sort_order": 3,
        "powerbi_report_id": "PBI-YTD-PERFORMANCE",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-YTD-PERFORMANCE",
    },
    {
        "report_group_slug": "topline-financials",
        "name": "Monthly Profitability",
        "slug": "monthly-profitability",
        "description": "Monthly profitability analysis covering GOP, NOP, and margins.",
        "sort_order": 4,
        "powerbi_report_id": "PBI-MONTHLY-PROFITABILITY",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-MONTHLY-PROFITABILITY",
    },
    {
        "report_group_slug": "distribution",
        "name": "Channel Contribution",
        "slug": "channel-contribution",
        "description": "Revenue, room nights, and ADR contribution by booking channel.",
        "sort_order": 1,
        "powerbi_report_id": "PBI-CHANNEL-CONTRIBUTION",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-CHANNEL-CONTRIBUTION",
    },
    {
        "report_group_slug": "distribution",
        "name": "Direct vs OTA Performance",
        "slug": "direct-vs-ota-performance",
        "description": "Comparison of direct channels against OTAs for production and cost efficiency.",
        "sort_order": 2,
        "powerbi_report_id": "PBI-DIRECT-VS-OTA",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-DIRECT-VS-OTA",
    },
    {
        "report_group_slug": "distribution",
        "name": "Channel Cost of Acquisition",
        "slug": "channel-cost-of-acquisition",
        "description": "Commission, acquisition cost, and net revenue analysis by channel.",
        "sort_order": 3,
        "powerbi_report_id": "PBI-CHANNEL-COA",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-CHANNEL-COA",
    },
    {
        "report_group_slug": "segmentation",
        "name": "Segment Mix Analysis",
        "slug": "segment-mix-analysis",
        "description": "Business mix by segment with room nights, ADR, and revenue contribution.",
        "sort_order": 1,
        "powerbi_report_id": "PBI-SEGMENT-MIX",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-SEGMENT-MIX",
    },
    {
        "report_group_slug": "segmentation",
        "name": "Segment ADR & Revenue",
        "slug": "segment-adr-revenue",
        "description": "ADR and revenue comparison across market segments.",
        "sort_order": 2,
        "powerbi_report_id": "PBI-SEGMENT-ADR-REV",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-SEGMENT-ADR-REV",
    },
    {
        "report_group_slug": "segmentation",
        "name": "Rate Code Performance",
        "slug": "rate-code-performance",
        "description": "Performance by rate code, promo, and pricing category.",
        "sort_order": 3,
        "powerbi_report_id": "PBI-RATE-CODE-PERFORMANCE",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-RATE-CODE-PERFORMANCE",
    },
    {
        "report_group_slug": "forecasting-budget",
        "name": "Daily Forecast",
        "slug": "daily-forecast",
        "description": "Daily forecast of occupancy, ADR, and revenue.",
        "sort_order": 1,
        "powerbi_report_id": "PBI-DAILY-FORECAST",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-DAILY-FORECAST",
    },
    {
        "report_group_slug": "forecasting-budget",
        "name": "Monthly Forecast",
        "slug": "monthly-forecast",
        "description": "Monthly projection of room nights, occupancy, ADR, RevPAR, and revenue.",
        "sort_order": 2,
        "powerbi_report_id": "PBI-MONTHLY-FORECAST",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-MONTHLY-FORECAST",
    },
    {
        "report_group_slug": "forecasting-budget",
        "name": "Forecast Accuracy",
        "slug": "forecast-accuracy",
        "description": "Variance analysis between forecasted and actual performance.",
        "sort_order": 3,
        "powerbi_report_id": "PBI-FORECAST-ACCURACY",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-FORECAST-ACCURACY",
    },
    {
        "report_group_slug": "account-management",
        "name": "Top Account Production",
        "slug": "top-account-production",
        "description": "Production by top corporate, travel agent, and wholesale accounts.",
        "sort_order": 1,
        "powerbi_report_id": "PBI-TOP-ACCOUNT-PRODUCTION",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-TOP-ACCOUNT-PRODUCTION",
    },
    {
        "report_group_slug": "account-management",
        "name": "Corporate Account Performance",
        "slug": "corporate-account-performance",
        "description": "Performance analysis of negotiated corporate accounts.",
        "sort_order": 2,
        "powerbi_report_id": "PBI-CORP-ACCOUNT-PERFORMANCE",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-CORP-ACCOUNT-PERFORMANCE",
    },
    {
        "report_group_slug": "account-management",
        "name": "Agency & TMC Production",
        "slug": "agency-tmc-production",
        "description": "Travel management company and agency contribution reporting.",
        "sort_order": 3,
        "powerbi_report_id": "PBI-AGENCY-TMC-PRODUCTION",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-AGENCY-TMC-PRODUCTION",
    },
    {
        "report_group_slug": "booking-activity-patterns",
        "name": "Booking Pickup",
        "slug": "booking-pickup",
        "description": "Daily and period pickup tracking by stay date and booking date.",
        "sort_order": 1,
        "powerbi_report_id": "PBI-BOOKING-PICKUP",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-BOOKING-PICKUP",
    },
    {
        "report_group_slug": "booking-activity-patterns",
        "name": "Pace Analysis",
        "slug": "pace-analysis",
        "description": "On-the-books and pace analysis versus budget and last year.",
        "sort_order": 2,
        "powerbi_report_id": "PBI-PACE-ANALYSIS",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-PACE-ANALYSIS",
    },
    {
        "report_group_slug": "booking-activity-patterns",
        "name": "Lead Time Analysis",
        "slug": "lead-time-analysis",
        "description": "Booking window and lead time trends by segment and channel.",
        "sort_order": 3,
        "powerbi_report_id": "PBI-LEAD-TIME-ANALYSIS",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-LEAD-TIME-ANALYSIS",
    },
    {
        "report_group_slug": "booking-activity-patterns",
        "name": "Length of Stay Patterns",
        "slug": "length-of-stay-patterns",
        "description": "Analysis of stay patterns, arrival day behavior, and shoulder nights.",
        "sort_order": 4,
        "powerbi_report_id": "PBI-LOS-PATTERNS",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-LOS-PATTERNS",
    },
    {
        "report_group_slug": "cancellation-no-show",
        "name": "Cancellation Analysis",
        "slug": "cancellation-analysis",
        "description": "Cancellation volume, value, timing, and channel behavior.",
        "sort_order": 1,
        "powerbi_report_id": "PBI-CANCELLATION-ANALYSIS",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-CANCELLATION-ANALYSIS",
    },
    {
        "report_group_slug": "cancellation-no-show",
        "name": "No-Show Report",
        "slug": "no-show-report",
        "description": "No-show count, value, and recovery tracking.",
        "sort_order": 2,
        "powerbi_report_id": "PBI-NO-SHOW-REPORT",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-NO-SHOW-REPORT",
    },
    {
        "report_group_slug": "cancellation-no-show",
        "name": "Wash Analysis",
        "slug": "wash-analysis",
        "description": "Wash trends across transient, group, and account business.",
        "sort_order": 3,
        "powerbi_report_id": "PBI-WASH-ANALYSIS",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-WASH-ANALYSIS",
    },
    {
        "report_group_slug": "pricing-inventory",
        "name": "BAR & Rate Position",
        "slug": "bar-rate-position",
        "description": "Best available rate ladder, rate position, and pricing comparisons.",
        "sort_order": 1,
        "powerbi_report_id": "PBI-BAR-RATE-POSITION",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-BAR-RATE-POSITION",
    },
    {
        "report_group_slug": "pricing-inventory",
        "name": "Inventory Status",
        "slug": "inventory-status",
        "description": "Sellable inventory, blocked rooms, out-of-order rooms, and room type availability.",
        "sort_order": 2,
        "powerbi_report_id": "PBI-INVENTORY-STATUS",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-INVENTORY-STATUS",
    },
    {
        "report_group_slug": "pricing-inventory",
        "name": "Restriction Controls",
        "slug": "restriction-controls",
        "description": "LOS rules, stop-sell, CTA/CTD, and blackout date reporting.",
        "sort_order": 3,
        "powerbi_report_id": "PBI-RESTRICTION-CONTROLS",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-RESTRICTION-CONTROLS",
    },
    {
        "report_group_slug": "demand-supply-market-share",
        "name": "Demand Trends",
        "slug": "demand-trends",
        "description": "Demand analysis by date, segment, and channel.",
        "sort_order": 1,
        "powerbi_report_id": "PBI-DEMAND-TRENDS",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-DEMAND-TRENDS",
    },
    {
        "report_group_slug": "demand-supply-market-share",
        "name": "Supply & Availability",
        "slug": "supply-availability",
        "description": "Supply-side reporting including available rooms, constraints, and OOO impact.",
        "sort_order": 2,
        "powerbi_report_id": "PBI-SUPPLY-AVAILABILITY",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-SUPPLY-AVAILABILITY",
    },
    {
        "report_group_slug": "demand-supply-market-share",
        "name": "Market Share Benchmark",
        "slug": "market-share-benchmark",
        "description": "Market share, MPI, ARI, and RGI benchmarking against comp set.",
        "sort_order": 3,
        "powerbi_report_id": "PBI-MARKET-SHARE-BENCHMARK",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-MARKET-SHARE-BENCHMARK",
    },
    {
        "report_group_slug": "geo-source-market-mix",
        "name": "Geo Source Performance",
        "slug": "geo-source-performance",
        "description": "Revenue, room nights, and ADR by country, city, and feeder market.",
        "sort_order": 1,
        "powerbi_report_id": "PBI-GEO-SOURCE-PERFORMANCE",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-GEO-SOURCE-PERFORMANCE",
    },
    {
        "report_group_slug": "geo-source-market-mix",
        "name": "Nationality & Residency Mix",
        "slug": "nationality-residency-mix",
        "description": "Guest contribution by nationality and country of residence.",
        "sort_order": 2,
        "powerbi_report_id": "PBI-NATIONALITY-RESIDENCY-MIX",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-NATIONALITY-RESIDENCY-MIX",
    },
    {
        "report_group_slug": "geo-source-market-mix",
        "name": "Source Market Trends",
        "slug": "source-market-trends",
        "description": "Trend analysis of source markets over time with growth and decline signals.",
        "sort_order": 3,
        "powerbi_report_id": "PBI-SOURCE-MARKET-TRENDS",
        "workspace_id": "",
        "dataset_id": "",
        "embed_url": "https://app.powerbi.com/reportEmbed?reportId=PBI-SOURCE-MARKET-TRENDS",
    },
]


class Command(BaseCommand):
    help = "Seed Power BI report groups and reports."

    def handle(self, *args, **options):
        properties = list(Property.objects.filter(is_active=True))
        if not properties:
            self.stdout.write(
                self.style.WARNING("No properties available. Run seed_properties first.")
            )
            return

        groups_by_slug = self.seed_report_groups()
        self.seed_property_subscriptions(properties, groups_by_slug.values())
        self.seed_reports(groups_by_slug)

        self.stdout.write(self.style.SUCCESS("Power BI report catalog seeded successfully."))

    def seed_report_groups(self):
        groups_by_slug = {}

        for payload in REPORT_GROUPS:
            group, created = ReportGroup.objects.update_or_create(
                slug=payload["slug"],
                defaults={
                    "name": payload["name"],
                    "description": payload["description"],
                    "sort_order": payload["sort_order"],
                    "icon": payload["icon"],
                    "color": payload["color"],
                    "is_active": True,
                },
            )
            groups_by_slug[payload["slug"]] = group
            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Created' if created else 'Updated'} group: {group.name}"
                )
            )

        return groups_by_slug

    def seed_property_subscriptions(self, properties, groups):
        for property_obj in properties:
            for group in groups:
                PropertyReportGroupSubscription.objects.update_or_create(
                    property=property_obj,
                    report_group=group,
                    defaults={
                        "is_active": True,
                    },
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Subscribed {len(properties)} active properties to all seeded report groups."
            )
        )

    def seed_reports(self, groups_by_slug):
        for payload in REPORTS:
            report_group = groups_by_slug[payload["report_group_slug"]]

            report, created = PowerBIReport.objects.update_or_create(
                slug=payload["slug"],
                defaults={
                    "report_group": report_group,
                    "name": payload["name"],
                    "description": payload["description"],
                    "sort_order": payload["sort_order"],
                    "powerbi_report_id": payload["powerbi_report_id"],
                    "workspace_id": payload["workspace_id"],
                    "dataset_id": payload["dataset_id"],
                    "embed_url": payload["embed_url"],
                    "is_active": True,
                },
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Created' if created else 'Updated'} report: {report.name}"
                )
            )