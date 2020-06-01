from django.forms import ModelForm, Form, CharField
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.conf import settings
from django.core.exceptions import ValidationError
from core.models import *

class SignupForm(ModelForm):
    """Creates a user object."""

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password"]


    def clean_password(self):
        """Runs the password validators specified in settings."""

        validate_password(self.data["password"])
        return self.data["password"]

        
    def save(self):
        """Hash password before saving."""

        user = ModelForm.save(self, commit=False)
        user.set_password(self.cleaned_data.get("password"))
        user.save()



class LoginForm(Form):
    """Checks a set of credentials against the users."""

    email = CharField()
    password = CharField()

    def validate_credentials(self):
        """Validates the form using full_clean, and if it's valid, tries to
        authenticate the credentials. If that succeeds, the user is returned. If
        the form is invalid, or the credentials incorrect, ``False`` is
        returned."""

        if self.is_valid():
            user = authenticate(
                email=self.cleaned_data.get("email"),
                password=self.cleaned_data.get("password")
            )
            if user: return user
        self.add_error("email", "Invalid credentials.")
        return False



class UpdateEmailForm(ModelForm):
    """Updates a user's email."""

    class Meta:
        model = User
        fields = ["email"]
    
    password = CharField(required=True)

    def clean_password(self):
        """Checks that the supplied password is currect."""

        if not self.instance.check_password(self.data["password"]):
            self.add_error("password", "Password not correct.")
        return self.data["password"]



class UpdatePasswordForm(ModelForm):

    class Meta:
        model = User
        fields = []
    
    current = CharField(required=True)
    new = CharField(required=True)

    def clean_current(self):
        """Checks that the supplied current password is currect."""

        if not self.instance.check_password(self.data["current"]):
            self.add_error("current", "Current password not correct.")
        return self.data["current"]


    def clean_new(self):
        """Runs the password validators specified in settings."""

        validate_password(self.data["new"])
        return self.data["new"]


    def save(self):
        self.instance.set_password(self.cleaned_data.get("new"))
        self.instance.save()



class UpdateBasicSettingsForm(ModelForm):
    """Updates a user's basic settings."""

    class Meta:
        model = User
        fields = ["timezone", "day_ends"]

        