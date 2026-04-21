from apps.settings.mappings.management.commands.seed_mapping_defaults import Command as BaseSeedCommand


class Command(BaseSeedCommand):
    help = "Backward-compatible wrapper for seeding booking source defaults."

    def handle(self, *args, **options):
        options["domain"] = ["booking_source"]
        options["all_domains"] = False
        super().handle(*args, **options)
