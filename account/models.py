import datetime
from datetime import timedelta

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import AbstractBaseModel
from core.models.abstract_base_model import SoftDeleteObjectsManager
from core.validator import mobile_number_validation


class UserManager(BaseUserManager, SoftDeleteObjectsManager):
    def create_user(self, mobile_number, email, first_name='', last_name='', password=None):
        if mobile_number is None:
            raise TypeError("Users should have a username")
        if email is None:
            raise TypeError("Users should have a Email")

        user = self.model(
            mobile_number=mobile_number,
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(
            self,
            mobile_number,
            email,
            password=None,
    ):
        if password is None:
            raise TypeError("Password should not be none")
        if mobile_number is None:
            raise TypeError("Users should have a username")
        if email is None:
            raise TypeError("Users should have a Email")

        user = self.model(
            mobile_number=mobile_number,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_verified_mobile = True
        user.is_verified_email = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=16, unique=True, db_index=True, validators=[mobile_number_validation])
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_verified_mobile = models.BooleanField(default=False)
    is_verified_email = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["mobile_number"]

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class OTP(AbstractBaseModel):
    mobile_number = models.CharField(max_length=16, validators=[mobile_number_validation])
    otp = models.CharField(max_length=6)
    is_matched = models.BooleanField(default=False)
    duration = models.DurationField(
        default=timedelta(minutes=2)
    )

    @property
    def expired(self):
        if (
                self.created_at.replace(tzinfo=None) + self.duration
                < datetime.datetime.utcnow()
        ):
            return True
        else:
            return False


def __str__(self):
    return str(self.mobile_number)
