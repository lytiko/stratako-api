import jwt
import time
import pytz
from random import randint
from timezone_field import TimeZoneField
from django.conf import settings
from django.db import models

class BigIdModel(models.Model):
    """Provides a custom ID primary key field - a random 15 digit integer."""

    class Meta:
        abstract = True

    id = models.BigIntegerField(primary_key=True)

    def save(self, *args, **kwargs):
        """If the user hasn't provided an ID, generate one at random and check
        that it has not been taken."""
        
        digits = 18
        if not self.id:
            is_unique = False
            while not is_unique:
                id = randint(10 ** (digits - 1), 10 ** digits)
                is_unique = not self.__class__.objects.filter(id=id).exists()
            self.id = id
        super(BigIdModel, self).save(*args, **kwargs)