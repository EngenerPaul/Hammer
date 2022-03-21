from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Hammer_User(models.Model):
    """ User profile """

    phone = models.IntegerField(
        verbose_name='phone',
        unique=True,
        validators=(
            MinValueValidator(8_900_000_00_00),
            MaxValueValidator(8_999_999_99_99)
        )
    )
    personal_code = models.CharField(
        max_length=6,
        verbose_name='personal_code',
        unique=True
    )
    referral_code = models.CharField(
        max_length=6,
        verbose_name='referral_code',
        blank=True,
        null=True
    )
