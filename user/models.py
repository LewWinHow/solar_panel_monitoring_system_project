from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    AbstractUser,
)


class User(AbstractUser):
    GENDER_CHOICES = [
        (1, "Male"),
        (2, "Female")
    ]

    """
    -----AbstractUser-provided fields-----

    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField(default=False) //Mean administration login
    is_active = models.BooleanField(default=True) //Mean account status
    is_superuser = models.BooleanField(default=False) //Mean supervisor login
    last_login = models.DateTimeField(blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    """
    birthday = models.DateField(null=True, blank=True)
    gender = models.IntegerField(
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        db_comment="1 = Male, 2 = Female"
    )
    phone = models.CharField(max_length=13, unique=True, null=True, blank=True)
    profile = models.ImageField(upload_to="profile/", null=True, blank=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
