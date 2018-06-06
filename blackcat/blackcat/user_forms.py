from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, HiddenInput
from blackcat.storysharing.models import User


class CreateUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email", "username")
        labels = {"email": "Email"}
        help_texts = {"username": None}


class ProfileForm(ModelForm):

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {"username": HiddenInput()}
