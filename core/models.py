import time
import jwt
import base64
from random import randint
from django_random_id_model import RandomIDModel
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

class User(RandomIDModel):
    """The user model."""

    class Meta:
        db_table = "users"
        ordering = ["creation_time"]

    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=128)
    last_login = models.IntegerField(null=True, default=None)
    creation_time = models.IntegerField(default=0)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.email})"
    

    @staticmethod
    def from_token(token):
        """Takes a JWT, and if it's signed properly, isn't expired, and points
        to an actual user, returns that user."""

        try:
            token = jwt.decode(token, settings.SECRET_KEY)
            assert token["expires"] > time.time()
            user = User.objects.get(id=token["sub"])
        except: user = None
        return user
    

    def save(self, *args, **kwargs):
        """If the model is being saved for the first time, set the creation
        time."""
        
        if not self.id:
            self.creation_time = int(time.time())
        super(User, self).save(*args, **kwargs)
    

    def set_password(self, password):
        """"Sets the user's password, salting and hashing whatever is given
        using Django's built in functions."""

        self.password = make_password(password)
        self.save()
    

    def make_access_jwt(self):
        """Creates and signs an access token indicating the user who signed and
        the time it was signed. It will also indicate that it expires in 15
        minutes."""
        
        now = int(time.time())
        return jwt.encode({
            "sub": self.id, "iat": now, "expires": now + 900
        }, settings.SECRET_KEY, algorithm="HS256").decode()
    

    def make_refresh_jwt(self):
        """Creates and signs an refresh token indicating the user who signed and
        the time it was signed. It will also indicate that it expires in 365
        days."""
        
        now = int(time.time())
        return jwt.encode({
            "sub": self.id, "iat": now, "expires": now + 31536000
        }, settings.SECRET_KEY, algorithm="HS256").decode()



class Slot(RandomIDModel):

    class Meta:
        db_table = "slots"
        ordering = ["order"]

    name = models.CharField(max_length=40)
    order = models.IntegerField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="slots")

    def __str__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        """If no order is given, count the number of slots in the containing
        user and add one."""
        
        if self.order is None:
            self.order = self.user.slots.count() + 1
        super(Slot, self).save(*args, **kwargs)
    

    def move_to(self, index):
        """Moves a Slot to a new position within the containing user."""

        slots = list(self.user.slots.exclude(id=self.id))
        slots.insert(index, self)
        for i, slot in enumerate(slots, start=1):
            slot.order = i
        Slot.objects.bulk_update(slots, ["order"])



class Project(RandomIDModel):

    class Meta:
        db_table = "projects"
        ordering = ["creation_time"]

    STATUSES = [
        (1, "Not Started"),
        (2, "Active"),
        (3, "Maintenance"),
        (4, "Completed"),
        (5, "Abandoned")
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(default="")
    color = models.CharField(max_length=9)
    status = models.IntegerField(choices=STATUSES, default=2)
    creation_time = models.IntegerField(default=time.time)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")

    def __str__(self):
        return self.name