from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.test import TestCase
from django.urls import reverse
from .storysharing.test_views import create_random_user
import base64


def get_go_back_home_link():
    link = "<a href=\"{}\"> > Go back to the home page < </a>".format(
        reverse('index')
    )
    return link


class LoginViewTest(TestCase):

    def test_content(self):
        response = self.client.get(reverse('login'))
        self.assertContains(response, "-- Log in --")
        self.assertContains(response, "Username:")
        self.assertContains(response, "Password:")
        self.assertContains(response, "Submit")
        self.assertContains(response, "> Did you forget your password? <")
        self.assertContains(response, "<input")
        self.assertContains(response, "type=\"text\"")
        self.assertContains(response, "type='submit'")
        self.assertContains(response, "type=\"hidden\"")
        self.assertContains(response, reverse('lost_password'))


class LogoutViewTest(TestCase):

    def test_content(self):
        response = self.client.get(reverse('logout'))
        self.assertContains(response, "Thank you for logging out")
        self.assertContains(response, get_go_back_home_link())


class LostPasswordViewTest(TestCase):

    def test_content(self):
        response = self.client.get(reverse('lost_password'))
        self.assertContains(response, "-- Set a new password --")
        self.assertContains(response, "Email:")
        self.assertContains(
            response,
            "You will receive an email with instructions to follow"
        )
        self.assertContains(response, "Submit")
        self.assertContains(response, "<input")
        self.assertContains(response, 'type="email"')
        self.assertContains(response, "type='submit'")


class LostPasswordDoneViewTest(TestCase):

    def test_content(self):
        response = self.client.get(reverse('lost_password_done'))
        self.assertContains(response, "Check your email (and spam folder).")
        self.assertContains(response, get_go_back_home_link())


class ChangePasswordViewTest(TestCase):

    def test_content(self):
        user = create_random_user()
        self.client.login(username=user.username, password="password")
        response = self.client.get(reverse('change_password'))
        self.assertContains(response, "Old password:")
        self.assertContains(response, "New password:")
        self.assertContains(response, "New password confirmation:")
        self.assertContains(
            response,
            "be too similar to your other personal information."
        )
        self.assertContains(
            response,
            "Your password must contain at least 8 characters."
        )
        self.assertContains(
            response,
            "be a commonly used password."
        )
        self.assertContains(
            response,
            "be entirely numeric."
        )
        self.assertContains(response, "Submit")
        self.assertContains(response, "<input")
        self.assertContains(response, "type='submit'")

    def test_requries_login(self):
        self.client.logout()
        response = self.client.get(reverse('change_password'))
        self.assertEqual(response.status_code, 302)


class ChangePasswordDoneViewTest(TestCase):

    def test_content(self):
        user = create_random_user()
        self.client.login(username=user.username, password="password")
        response = self.client.get(reverse('change_password_done'))
        self.assertContains(response, "Thank you for changing your password")
        self.assertContains(response, get_go_back_home_link())


class ResetPasswordViewTest(TestCase):

    def test_content(self):
        # user = create_random_user()
        # token = PasswordResetTokenGenerator().make_token(user)
        # uidb64 = base64.urlsafe_b64encode(bytes([user.id]))
        # response = self.client.get(reverse('reset_password', kwargs={
        #     'uidb64': uidb64,
        #     'token': token
        # }))
        # self.assertContains(response, "-- Reset your password --")
        # self.assertContains(response, "New Password:")
        # self.assertContains(response, "Submit")
        pass


class ResetPasswordDoneViewTest(TestCase):

    def test_content(self):
        response = self.client.get(reverse('reset_password_done'))
        self.assertContains(response, "Your password has been reset")
        self.assertContains(response, get_go_back_home_link())
