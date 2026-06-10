from random import choices

from django.db import models


class LoginInfo(models.Model):
    BLACKLIST_CHOICES = [
        (0, "None"),
        (1, "Yes"),
    ]

    BOT_CHOICES = [
        (0, "None"),
        (1, "Yes"),
    ]

    ip = models.GenericIPAddressField()
    system = models.CharField(max_length=150)
    device = models.CharField(max_length=150)
    is_bot = models.IntegerField(choices=BOT_CHOICES, db_comment="0 = None, 1 = Yes")
    failed_count = models.IntegerField(default=0)
    blacklist = models.IntegerField(choices=BLACKLIST_CHOICES, default=0)

    class Meta:
        db_table = "login_info"


class LoginRecord(models.Model):
    STATUS_CHOICES = [
        (0, "Failed"),
        (1, "Successful")
    ]

    login_info = models.ForeignKey("LoginInfo", on_delete=models.CASCADE)
    username = models.CharField(max_length=150, null=True, blank=True)
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        db_comment="0 = Failed, 1 = Successful"
    )
    recorded_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "login_record"


class LoginReport(models.Model):
    month = models.IntegerField()
    year = models.IntegerField()
    generated_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "login_report"


class TotalContentOfLoginReport(models.Model):
    login_report = models.ForeignKey("LoginReport", on_delete=models.CASCADE, related_name="total_content_of_login_report")
    total_login_count = models.IntegerField()
    total_login_successful = models.IntegerField()
    total_login_failed = models.IntegerField()

    class Meta:
        db_table = "total_content_of_login_report"

class BlacklistContentOfLoginReport(models.Model):
    login_report = models.ForeignKey("LoginReport", on_delete=models.CASCADE, related_name="blacklist_content_of_login_report")
    login_info = models.ForeignKey("LoginInfo", on_delete=models.CASCADE, related_name="blacklist_content_of_login_info")

    class Meta:
        db_table = "blacklist_content_of_login_report"
