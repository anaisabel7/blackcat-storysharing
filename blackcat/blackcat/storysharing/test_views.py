from django.contrib.auth import login
from django.urls import reverse
from django.test import TestCase
from .models import User, Story


def create_random_user():
    user = User.objects.create(
        username='randomuser', email='random@email.com'
    )
    user.set_password('password')
    user.save()
    return user


class IndexViewTest(TestCase):

    def test_base_content(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, "Welcome to")
        self.assertContains(response, "Black Cat")
        self.assertContains(response, "Story Sharing")
        self.assertContains(response, "Would you like to...?")
        self.assertContains(response, "Take a look at our public stories")
        self.assertContains(response, reverse("stories"))
        self.assertContains(
            response, "Create a user / Log in to start"
        )
        self.assertContains(response, "playing!")

    def test_content_change_for_logged_in_user(self):
        user = create_random_user()
        self.client.login(username=user.username, password='password')
        response = self.client.get(reverse('index'))
        self.assertNotIn(
            "Create a user / Log in to start playing!", str(response.content)
        )
        self.assertContains(response, "Visit your profile to start")
        self.assertContains(response, "playing!")


class PublicStoriesViewTest(TestCase):
    def test_content_without_public_stories(self):
        response = self.client.get(reverse('stories'))
        self.assertContains(response, "Stories")
        story = Story.objects.create(title="Wonderful Story")
        user = create_random_user()
        story.writers.add(user)
        private_story_response = self.client.get(reverse('stories'))
        self.assertEqual(
            str(response.content),
            str(private_story_response.content)
        )

    def test_content_with_public_stories(self):
        response = self.client.get(reverse('stories'))
        story = Story.objects.create(title="Wonderful Story", public=True)
        user = create_random_user()
        story.writers.add(user)
        public_story_response = self.client.get(reverse('stories'))
        self.assertNotEqual(
            str(response.content),
            str(public_story_response.content)
        )
        self.assertContains(public_story_response, "Stories")
        self.assertContains(public_story_response, story.title)
        self.assertContains(
            public_story_response, story.writers.get_queryset()[0].username
        )


class PersonalStoriesViewTest(TestCase):

    def test_displaying_stories_writen_by_user_only(self):
        user = create_random_user()
        self.client.login(username=user.username, password='password')
        story = Story.objects.create(title="A story my user wrote.")
        story.writers.add(user)
        other_user = User.objects.create(
            username='otheruser', email="an@email.com"
        )
        other_story = Story.objects.create(title="Other story")
        other_story.writers.add(other_user)
        response = self.client.get(reverse('personal'))
        self.assertContains(response, "Stories")
        self.assertContains(response, story.title)
        self.assertContains(response, user.username)
        self.assertNotIn(other_user.username, str(response.content))
        self.assertNotIn(other_story.title, str(response.content))


class BaseContentTest(TestCase):
    pass
