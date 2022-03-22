from datetime import datetime
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.core import validators
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

import jwt


class UserManager(BaseUserManager):
    """ This manager is used in the User class """

    def _create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError(
                "This phone does'n exist"
            )

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must have is_superuser=True.'
            )

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """ Main user class """

    username = models.BigIntegerField(
        verbose_name='phone',
        unique=True,
        validators=(
            MinValueValidator(8_900_000_00_00),
            MaxValueValidator(8_999_999_99_99)
        )
    )
    email = models.EmailField(
        _('email address'),
        # unique=True,
        blank=True
        )
    confirm_code = models.IntegerField(
        blank=True,
        null=True,
        validators=(
            MinValueValidator(1_000),
            MaxValueValidator(9_999)
        )
    )
    personal_code = models.CharField(
        max_length=6,
        verbose_name='personal_code',
        unique=True,
        blank=True,
        null=True,
    )
    referral_code = models.CharField(
        max_length=6,
        verbose_name='referral_code',
        blank=True,
        null=True
    )
    token = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    is_staff = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'  # this field is used to enter
    REQUIRED_FIELDS = ['email']

    # class UserManager must manage objects of this type
    objects = UserManager()

    def __str__(self):
        return str(self.username)

    @property
    def get_token(self):
        return self._generate_jwt_token()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=60)

        token = jwt.encode({
            'id': self.pk,
            'exp': dt
        }, settings.SECRET_KEY, algorithm='HS256')

        return token
        # return token.decode('utf-8')
