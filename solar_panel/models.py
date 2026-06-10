from django.db import models


class SolarPanel(models.Model):
    STATUS_CHOICES = [(0, "No Active"), (1, "Active")]

    name = models.CharField(
        max_length=150,
    )
    zone = models.IntegerField()
    position = models.IntegerField()
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        db_comment="0 = No Active, 1 = Active"
    )
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "solar_panel"


class SolarPanelMonitoring(models.Model):

    DAMAGE_CHOICES = [
        (0, "None"),
        (1, "Yes"),
    ]

    CLEANLINESS_CHOICES = [
        (1, "Clean"),
        (2, "Dirty"),
        (3, "Bird Drop")
    ]

    solar_panel = models.ForeignKey(
        "SolarPanel",
        on_delete=models.CASCADE,
        related_name="solar_panel_monitoring"
    )
    damage = models.IntegerField(choices=DAMAGE_CHOICES, db_comment="0 = None, 1 = Yes")
    cleanliness = models.IntegerField(choices=CLEANLINESS_CHOICES,
                                      db_comment="1 = Clean, 2 = Dusty, 3 = Bird Drop")
    image = models.ImageField(upload_to="detect_solar_panel_result/",)

    class Meta:
        db_table = "solar_panel_monitoring"


class SolarPanelRecord(models.Model):
    DAMAGE_CHOICES = [
        (0, "None"),
        (1, "Yes"),
    ]

    CLEANLINESS_CHOICES = [
        (1, "Clean"),
        (2, "Dusty"),
        (3, "Bird Drop")
    ]

    solar_panel = models.ForeignKey("SolarPanel", on_delete=models.CASCADE, related_name="solar_panel_record")
    damage = models.IntegerField(choices=DAMAGE_CHOICES, db_comment="0 = None, 1 = Yes")
    cleanliness = models.IntegerField(choices=CLEANLINESS_CHOICES,
                                      db_comment="1 = Clean, 2 = Dusty, 3 = Bird Drop")
    image = models.ImageField(upload_to="detect_solar_panel_result/")
    recorded_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "solar_panel_record"


class SolarPanelReport(models.Model):
    month = models.IntegerField()
    year = models.IntegerField()
    generated_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "solar_panel_report"

class WarningSolarPanel(models.Model):
    STATUS_CHOICES = [(1,"Temperature High"),(2,"Temperature Too High"),(3,"Fire")]
    solar_panel_id = models.IntegerField()
    status = models.IntegerField(choices=STATUS_CHOICES)
    temperature = models.FloatField()

    class Meta:
        db_table = "warning_solar_panel"

class ContentOfSolarPanelReport(models.Model):
    solar_panel_report = models.ForeignKey("SolarPanelReport", on_delete=models.CASCADE,)
    total_solar_panel = models.IntegerField()
    total_damage = models.IntegerField()
    total_clean = models.IntegerField()
    total_dusty = models.IntegerField()
    total_bird_drop = models.IntegerField()

    class Meta:
        db_table = "content_of_solar_panel_report"

class SolarPanelDetectVideo(models.Model):
    video = models.FileField(upload_to="detect_solar_panel_result/")
    recorded_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "solar_panel_detect_video"