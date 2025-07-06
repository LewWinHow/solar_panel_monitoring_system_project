from django.core.management.base import BaseCommand
from monitoring.models import SolarPanel, TemperatureRecord, MonitoringTemperature
from django.utils.timezone import now


class Command(BaseCommand):
    help = "Record temperature snapshot for each panel into TemperatureRecord table."

    def handle(self, *args, **kwargs):
        panels = MonitoringTemperature.objects.select_related("solar_panel")

        for monitoring in panels:
            TemperatureRecord.objects.create(
                solar_panel=monitoring.solar_panel,
                temperature=monitoring.temperature,
                status=monitoring.status,
                damage=monitoring.damage,
                cleanliness=monitoring.cleanliness,
                recorded_time=now(),
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"{len(panels)} temperature snapshots recorded at {now()}"
            )
        )
