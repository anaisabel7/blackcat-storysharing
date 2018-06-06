from django.template import loader
from django.test import TestCase
from django.urls import reverse
from django.utils.html import escape
from blackcat.storysharing.models import User
from blackcat.storysharing.test_views import create_random_user


def get_go_back_home_link():
    link = "<a href=\"{}\"> > Go back to the home page < </a>".format(
        reverse('index')
    )
    return link


def get_password_warnings():
    warnings = [
        "be too similar to your other personal information.",
        "Your password must contain at least 8 characters.",
        "be a commonly used password.",
        "be entirely numeric."
    ]
    return warnings


class LoginViewTest(TestCase):

    def test_content(self):
        response = self.client.get(reverse('login'))
        self.assertContains(response, "-- Log in --")
        self.assertContains(response, "Username:")
        self.assertContains(response, "Password:")
        self.assertContains(response, "Submit")
        self.assertContains(response, "> Did you forget your password? <")
        self.assertContains(response, "> Create a new user. < ")
        self.assertContains(response, "<input")
        self.assertContains(response, "type=\"text\"")
        self.assertContains(response, "type='submit'")
        self.assertContains(response, "type=\"hidden\"")
        self.assertContains(response, reverse('lost_password'))
        self.assertContains(response, reverse('create_user'))


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

        password_warnings = get_password_warnings()
        for warning in password_warnings:
            self.assertContains(response, warning)

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
        tmp_response = self.client.get(reverse('reset_password', kwargs={
            'uidb64': 'NA',
            'token': 'set-password'
        }))

        context = tmp_response.context[0].flatten()
        context['validlink'] = True
        template = loader.get_template("user/reset_password.html")
        response_content = template.render(context)
        self.assertIn("-- Reset your password --", response_content)
        self.assertIn("Submit", response_content)
        self.assertIn("<form method=\"post\">", response_content)
        self.assertIn("<input type='submit'", response_content)

    def test_cotnent_for_invalid_link(self):
        response = self.client.get(reverse('reset_password', kwargs={
            'uidb64': 'NA',
            'token': 'set-password'
        }))
        self.assertContains(response, "-- Invalid reset password link --")
        self.assertContains(response, "> Get a new reset password link <")
        self.assertContains(response, reverse('lost_password'))


class ResetPasswordDoneViewTest(TestCase):

    def test_content(self):
        response = self.client.get(reverse('reset_password_done'))
        self.assertContains(response, "Your password has been reset")
        self.assertContains(response, get_go_back_home_link())


class CreateUserViewTest(TestCase):

    def test_content(self):
        response = self.client.get(reverse('create_user'))
        self.assertContains(response, "-- Create a new user --")
        self.assertContains(response, "Email:")
        self.assertContains(response, "Username:")
        self.assertContains(response, "Password:")
        self.assertContains(response, "Password confirmation:")
        self.assertContains(response, "Submit")
        self.assertContains(response, "<input type=\"submit\"")
        self.assertContains(response, "<form method=\"post\"")

    def test_post_invalid_form_reloads_form_with_warning_errors(self):
        post_data = {
            "email": "random@email.com",
            "username": "randomuser",
            "password1": "onepassword",
            "password2": "anotherpassword",
        }
        response = self.client.post(reverse('create_user'), data=post_data)
        self.assertContains(response, "-- Create a new user --")
        self.assertContains(response, "Email:")
        self.assertContains(response, "Username:")
        self.assertContains(response, "Password:")
        self.assertContains(response, "Password confirmation:")
        self.assertContains(
            response,
            escape("The two password fields didn't match.")
        )

    def test_post_valid_form_redirects_to_homepage_and_creates_user(self):

        self.assertEqual(User.objects.filter(username='randomuser').count(), 0)

        post_data = {
            "email": "random@email.com",
            "username": "randomuser",
            "password1": "onepassword",
            "password2": "onepassword",
            'csrfmiddlewaretoken': [
                '87cxzfj3CGaMaFczM6vumJ3D1d9zGWLqufrVhCQXBDBK6TYvRfte9hzln48wYRo4'
            ]
        }
        response = self.client.post(
            reverse('create_user'), data=post_data, follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(User.objects.filter(username='randomuser').count(), 1)

        user = User.objects.filter(username='randomuser')[0]
        self.assertEqual(user.email, "random@email.com")
        self.assertTrue(user.check_password('onepassword'))

    def test_post_valid_form_logging_users_out_and_in(self):

        prev_user = User.objects.create(
            username="previoususer", email="previous@email.com"
        )
        prev_user.set_password('password')
        prev_user.save()
        self.client.login(
            username=prev_user.username, password='password'
        )

        response = self.client.get(reverse('create_user'))

        self.assertEqual(response.context['user'].username, prev_user.username)

        post_data = {
            "email": "random@email.com",
            "username": "randomuser",
            "password1": "onepassword",
            "password2": "onepassword",
            'csrfmiddlewaretoken': [
                '87cxzfj3CGaMaFczM6vumJ3D1d9zGWLqufrVhCQXBDBK6TYvRfte9hzln48wYRo4'
            ]
        }

        response = self.client.post(
            reverse('create_user'), data=post_data, follow=True
        )

        self.assertNotEqual(
            response.context['user'].username, prev_user.username
        )
        self.assertEqual(response.context['user'].username, "randomuser")
