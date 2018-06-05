from django.contrib.auth.forms import UserCreationForm
from blackcat.storysharing.models import User


class CreateUserForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("email", "username")
        labels = {"email": "Email"}
        help_texts = {"username": None}
