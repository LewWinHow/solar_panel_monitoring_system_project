from django.db import models

class LoginInfo(models.Model):
    BLACKLIST_CHOICES = [
        (0, "None"),
        (1, "Yes"),
    ]

    ip = models.GenericIPAddressField()
    mac = models.CharField(max_length=150)
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
    password = models.CharField(max_length=128, null=True, blank=True)
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
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "login_report"
