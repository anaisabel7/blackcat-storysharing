from blackcat.storysharing.models import User
from django.forms import HiddenInput
from django.test import TestCase
from .user_forms import CreateUserForm, ProfileForm


class CreateUserFormTest(TestCase):
    def test_meta_data(self):
        self.assertEqual(CreateUserForm._meta.model, User)

        expected_fields = ['username', 'email']
        for field in expected_fields:
            self.assertIn(field, CreateUserForm._meta.fields)

        self.assertIn('email', CreateUserForm._meta.fields)
        self.assertEqual(CreateUserForm._meta.labels['email'], "Email")

        self.assertIn('username', CreateUserForm._meta.help_texts)
        self.assertEqual(CreateUserForm._meta.help_texts['username'], None)


class ProfileFormTest(TestCase):
    def test_meta_data(self):
        self.assertEqual(ProfileForm._meta.model, User)

        expected_fields = ["username", "email"]
        for field in expected_fields:
            self.assertIn(field, ProfileForm._meta.fields)

        self.assertIn('username', ProfileForm._meta.widgets)
        self.assertTrue(isinstance(
            ProfileForm._meta.widgets['username'], HiddenInput
        ))
