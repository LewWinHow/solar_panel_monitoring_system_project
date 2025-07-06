from django.db import models


class SolarPanel(models.Model):
    STATUS_CHOICES = [(0, "No Active"), (1, "Active")]

    name = models.CharField(
        max_length=150,
    )
    zone = models.IntegerField()
    position = models.IntegerField()
    temperature_threshold = models.FloatField(db_comment="The maximum temperature that solar panels can withstand")
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        db_comment="0 = No Active, 1 = Active"
    )
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "solar_panel"


class SolarPanelMonitoring(models.Model):
    STATUS_CHOICES = [
        (1, "Normal"),
        (2, "Temperature High"),
        (3, "Temperature Too High"),
        (4, "Stop Run"),
        (5, "Fire"),
        (6, "Unknown")
    ]

    DAMAGE_CHOICES = [
        (0, "None"),
        (1, "Yes"),
        (2, "Unknown")
    ]

    CLEANLINESS_CHOICES = [
        (1, "Clean"),
        (2, "Dirty"),
        (3, "Very Dirty"),
        (4, "Unknown")
    ]

    solar_panel = models.ForeignKey(
        "SolarPanel",
        on_delete=models.CASCADE,
        related_name="solar_panel_monitoring"
    )
    temperature = models.FloatField()
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 db_comment="1 = Normal, 2 = Temperature High, 3 = Temperature Too High, 4 = Stop Run, 5 = Fire, 6 = Unknown")
    damage = models.IntegerField(choices=DAMAGE_CHOICES, db_comment="0 = None, 1 = Yes, 2 = Unknown")
    cleanliness = models.IntegerField(choices=CLEANLINESS_CHOICES,
                                      db_comment="1 = Clean, 2 = Dirty, 2 = Very Dirty, 3 = Unknown")

    class Meta:
        db_table = "solar_panel_monitoring"


class SolarPanelRecord(models.Model):
    STATUS_CHOICES = [
        (1, "Normal"),
        (2, "Temperature High"),
        (3, "Temperature Too High"),
        (4, "Stop Run"),
        (5, "Fire"),
        (6, "Unknown")
    ]

    DAMAGE_CHOICES = [
        (0, "None"),
        (1, "Yes"),
        (2, "Unknown")
    ]

    CLEANLINESS_CHOICES = [
        (1, "Clean"),
        (2, "Dirty"),
        (3, "Very Dirty"),
        (4, "Unknown")
    ]

    solar_panel = models.ForeignKey("SolarPanel", on_delete=models.CASCADE, related_name="solar_panel_record")
    temperature = models.FloatField()
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 db_comment="1 = Normal, 2 = Temperature High, 3 = Temperature Too High, 4 = Stop Run, 5 = Fire, 6 = Unknown")
    damage = models.IntegerField(choices=DAMAGE_CHOICES, db_comment="0 = None, 1 = Yes, 2 = Unknown")
    cleanliness = models.IntegerField(choices=CLEANLINESS_CHOICES,
                                      db_comment="1 = Clean, 2 = Dirty, 2 = Very Dirty, 3 = Unknown")
    recorded_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "solar_panel_record"


class ZoneTemperatureSnapshot(models.Model):
    zone = models.IntegerField()
    avg_temperature = models.FloatField()
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "zone_temperature_snapshot"

    def __str__(self):
        return f"Zone {self.zone} @ {self.created_time}"


class SolarPanelReportt(models.Model):
    month = models.IntegerField()
    year = models.IntegerField()
    generated_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "solar_panel_report"


class AVGTemperatureByTime(models.Model):
    recorded_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "avg_temperature_by_time"


class AVGTemperatureByZone(models.Model):
    AVGTemperatureByTime = models.ForeignKey("AVGTemperatureByTime", on_delete=models.CASCADE,
                                             related_name="avg_temperature_by_zone")
    zone = models.IntegerField()
    avg_temperature = models.FloatField()

    class Meta:
        db_table = "avg_temperature_by_zone"
