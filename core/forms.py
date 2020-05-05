import re
from django import forms
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.db.models import fields
from django.forms.models import ModelMultipleChoiceField
from core.models import *

class StratakoForm(forms.ModelForm):
    """A Django Model Form, with a few extra features.

    If it is being used to edit an existing object, it will accept data dicts
    that are missing required values, by just grabbing the missing values from
    the instance.

    It also blocks attempts to alter a user attribute on an existing object.

    If the associated model has a parent object that is not the user, it will
    add a cleaning method to it that prevents that attribute being assigned to
    another user.

    If it is being used to create a new object, it will allow missing required
    fields if they have a default value in the model.

    It also keeps a record of the orignal data dict as submitted, before missing
    values were added."""

    def __init__(self, data, *args, **kwargs):
        # Do the basic django modelform initialisation
        forms.ModelForm.__init__(self, data, *args, **kwargs)

        # Make a record of what was actually sent
        self.submitted_data = {**data}

        # If this is updating not creating, fill in any missing values
        if "instance" in kwargs:
            for field in self.base_fields:
                if field not in data:
                    value = getattr(kwargs["instance"], field)
                    try:
                        data[field] = value.id
                    except AttributeError:
                        try:
                            data[field] = value.all()
                        except AttributeError:
                            data[field] = value
        
        # If this is creating, use model default values where needed
        model_fields = {f.name: f for f in self.instance._meta.fields}
        if "instance" not in kwargs:
            for field in self.base_fields:
                if field not in data and field == "timezone":
                    data[field] = get_current_timezone().zone
                if field not in data and field in model_fields:
                    if model_fields[field].default != fields.NOT_PROVIDED:
                        data[field] = model_fields[field].default
                
        # Add clean_x methods for any fields that link to the user
        for path in self._meta.model.user_paths:
            if "__" in path:
                parent =  path.split('__')[0]
                setattr(self, f"clean_{parent}",
                 lambda parent=parent: self.clean_parent(parent))
        
        
    def clean_user(self):
        """If the form is editing an existing object, and the sender is trying
        to update the user, stop them."""

        if self.instance.id is not None and "user" in self.submitted_data:
            raise ValidationError("Cannot edit user")
        return self.cleaned_data["user"]
    

    def clean_parent(self, attribute):
        """Prevents an object's non-user parent being switched to the parent of
        another user."""

        if self.instance.id is not None and attribute in self.submitted_data:
            current_user = getattr(self.instance, attribute).user_id
            proposed_user = self.cleaned_data[attribute].user_id
            if current_user != proposed_user:
                raise ValidationError(f"{attribute} does not exist")
        return self.cleaned_data[attribute]
    

    def clean(self):
        """The clean method is used to make sure field combinations are correct.
        In this case it is used to make sure that the many to many fields on tag
        forms are consistent with the users of their associated objects.
        
        For every field in the form, it looks for many to many fields, then goes
        through every associated object, and ensures that their user matches the
        tag user."""

        forms.ModelForm.clean(self)
        for field in self.base_fields:
            if self.base_fields[field].__class__ is ModelMultipleChoiceField:
                for model in self.cleaned_data[field]:
                    model = getattr(model, model.user_paths[0].split("__")[0])\
                     if "__" in model.user_paths[0] else model
                    if self.cleaned_data["user"].id != model.user_id:
                        raise ValidationError("Tag doesn't match user")



class UserForm(StratakoForm):
    """Handles data for a User object. There are a few fields it doesn't allow
    to be modified, as the User model handles these itself.
    
    The only other customisation is for handling passwords - if the user sends
    a password, it will be hashed and that will be saved. Password length is
    validated too."""
    
    class Meta:
        model = User
        exclude = ["id", "date_joined", "groups", "user_permissions"]
    
    def __init__(self, data, *args, **kwargs):
        """Add validation for password length. This can't be done at the model
        level because the model never sees the password - only the hash."""

        StratakoForm.__init__(self, data, *args, **kwargs)
        self.fields["password"].validators.append(
         MinLengthValidator(8, message="Password must be at least 8 characters.")
        )

    
    def save(self):
        """Was a password sent? If so, hash before saving."""

        if "password" in self.submitted_data:
            user = StratakoForm.save(self, commit=False)
            user.set_password(self.cleaned_data.get("password"))
            user.save()
        else:
            user = forms.ModelForm.save(self)
        return user



class LoginForm(forms.Form):
    """Validates user credentials."""

    email = forms.CharField()
    password = forms.CharField()

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



class GoalForm(StratakoForm):
    
    class Meta:
        model = Goal
        exclude = ["id", "order", "goal_category"]