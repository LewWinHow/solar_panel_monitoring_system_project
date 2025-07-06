from django.core.management.base import BaseCommand
from solar_panel.models import SolarPanelRecord, SolarPanelReportt
from django.utils.timezone import now


class Command(BaseCommand):
    help = "Generate Monthly Solar Panel Report"

    def handle(self, *args, **options):
        current_time = now()
        month = current_time.month
        year = current_time.year

        records = SolarPanelRecord.objects.filter(
            recorded_time__year=year, recorded_time__month=month
        )

        total_panels = records.values("solar_panel").distinct().count()
        total_records = records.count()

        status_count = {
            1: records.filter(status=1).count(),
            2: records.filter(status=2).count(),
            3: records.filter(status=3).count(),
            4: records.filter(status=4).count(),
            5: records.filter(status=5).count(),
        }

        description = f"""
📊 {month}/{year} Temperature Monitoring Summary:
- Total panels: {total_panels}
- Total records: {total_records}
- Normal: {status_count[1]}
- High temperature: {status_count[2]}
- Overheated: {status_count[3]}
- Stopped: {status_count[4]}
- On fire: {status_count[5]}
"""

        report = SolarPanelReportt.objects.create(
            month=month, year=year, description=description
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Report generated for {month}/{year}, ID {report.id}"
            )
        )
        self.stdout.write(self.style.SUCCESS("Monthly report generation completed."))
