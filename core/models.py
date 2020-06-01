import jwt
import time
import pytz
from random import randint
from timezone_field import TimeZoneField
from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser

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



class User(AbstractUser, BigIdModel):
    """The user account model. Users require an email address as a username."""

    class Meta:
        db_table = "users"
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    is_staff = is_active = is_superuser = None

    day_ends = models.IntegerField(default=0, validators=[
        MaxValueValidator(5, message="Day end must be between 0 and 5"),
        MinValueValidator(0, message="Day end must be between 0 and 5")
    ])
    timezone = TimeZoneField(blank=True, default="", choices=[
        (tz, tz) for tz in pytz.all_timezones
    ])


    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
        
    
    def create_jwt(self):
        """Creates a JWT token for the user at the current UTC time.
        
        A JWT token consists of three components, separated by a period.
        
        The first is the header, which lists the algorithm used to encrypt,
        base64 encoded.
        
        The second is the payload, which contains information such as the name
        of the person the token represents, and the time the token was created.
        Again this is a dictionary, base64 encoded.
        
        The third segment is a secret which allows the server to verify that it
        issued this token at some point in the past. The first two sections are
        encrypted using some algorithm and the server's SECRET_KEY. When the
        token is encountered again, the server can confirm that encrypting the
        first two sections does indeed produce the third section."""

        return jwt.encode({
            "sub": self.id, "iat": int(time.time())
        }, settings.SECRET_KEY, algorithm="HS256").decode()