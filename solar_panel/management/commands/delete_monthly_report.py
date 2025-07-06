from django.core.management.base import BaseCommand
from solar_panel.models import SolarPanelReportt
from django.utils.timezone import now


class Command(BaseCommand):
    help = "Delete Monthly Solar Panel Report"

    def handle(self, *args, **options):
        current_time = now()
        month = current_time.month
        year = current_time.year

        reports = SolarPanelReportt.objects.filter(month=month, year=year)

        if not reports.exists():
            self.stdout.write(self.style.WARNING(f"❌ No report found for {month}/{year}."))
            return

        count = reports.count()
        reports.delete()

        self.stdout.write(self.style.SUCCESS(f"✅ Successfully deleted {count} report(s) for {month}/{year}."))
