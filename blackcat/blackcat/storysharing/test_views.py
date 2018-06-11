from django.contrib.auth import login
from django.urls import reverse
from django.test import TestCase
from .models import User, Story
from .urls import urlpatterns


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


class StartStoryViewTest(TestCase):
    def test_content(self):
        user = create_random_user()
        self.client.login(username=user.username, password="password")
        response = self.client.get(reverse('start_story'))
        self.assertContains(response, "-- Start a new story --")
        self.assertContains(response, "Title:")
        self.assertContains(response, "Writers:")
        self.assertContains(
            response,
            "Set this story as public, available for the world to see"
        )
        self.assertContains(response, "Create story")
        self.assertContains(response, "<form method=\"post\"")
        self.assertContains(response, "<input type=\"submit\"")

    def test_post_correct_form(self):
        user = create_random_user()
        self.client.login(username=user.username, password="password")
        post_data = {
            'title': "A story title",
            'writers': [user.id],
            'public': True
        }
        self.assertEqual(
            Story.objects.filter(title="A story title").count(), 0
        )
        response = self.client.post(reverse('start_story'), data=post_data)
        self.assertEqual(
            Story.objects.filter(title="A story title").count(), 1
        )
        story = Story.objects.filter(title="A story title")[0]
        self.assertEqual(story.writers.count(), 1)
        self.assertEqual(story.writers.all()[0], user)
        self.assertEqual(story.public, True)
        self.assertRedirects(
            response,
            reverse('display_story', kwargs={'id': story.id})
        )

    def test_post_incorrect_form(self):
        user = create_random_user()
        self.client.login(username=user.username, password="password")
        post_data = {
            'title': "Another story title",
            'writers': 'Eusebio',
            'public': True
        }
        self.assertEqual(
            Story.objects.filter(title="Another story title").count(),
            0
        )
        response = self.client.post(reverse('start_story'), data=post_data)
        self.assertContains(response, "Title:")
        self.assertContains(response, "Writers:")
        self.assertContains(
            response,
            "Set this story as public, available for the world to see"
        )
        self.assertContains(response, "Create story")

        self.assertIn('errors', response.context)
        self.assertContains(
            response,
            "There were some problems with the data introduced below."
        )
        self.assertContains(response, "The story has not been created")
        self.assertEqual(
            Story.objects.filter(title="Another story title").count(),
            0
        )

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse('start_story'))
        self.assertRedirects(
            response, reverse('login') + '?next=' + reverse('start_story')
        )


class BaseContentTest(TestCase):

    def test_header_displays_in_all_pages(self):
        user = create_random_user()
        self.client.login(username=user.username, password="password")
        headers = [
            '<meta name="viewport" {}>'.format(
                'content="width=device-width, initial-scale=1.0"'
            ),
            '<link rel="stylesheet" type="text/css" {}>'.format(
                'href="/static/storysharing/style.css"'
            )
        ]

        pages = [x.name for x in urlpatterns]
        pages.remove('logout')
        pages + ['logout']

        pages.remove('display_story')
        pages.remove('reset_password')

        pages.remove('jsi18n')
        for page in pages:
            response = self.client.get(reverse(page))
            for header in headers:
                self.assertContains(
                    response,
                    header
                )

        story = Story.objects.create(title="Awesome story")
        response = self.client.get(
            reverse('display_story', kwargs={'id': story.id})
        )
        for header in headers:
            self.assertContains(
                response,
                header
            )

        response = self.client.get(reverse(
            'reset_password', kwargs={'uidb64': 'NA', 'token': 'set-password'}
        ))
        for header in headers:
            self.assertContains(
                response,
                header
            )

    def test_menu_displays_in_all_pages(self):
        user = create_random_user()
        self.client.login(username=user.username, password="password")

        pages = [x.name for x in urlpatterns]
        pages.remove('logout')

        pages.remove('display_story')
        pages.remove('reset_password')

        pages.remove('jsi18n')
        for page in pages:
            response = self.client.get(reverse(page))
            self.assertContains(response, "<div class='menu'>")
            self.assertContains(response, reverse('index'))
            self.assertContains(response, reverse('stories'))
            self.assertContains(response, reverse('personal'))
            self.assertContains(response, reverse('profile'))
            self.assertContains(response, "Home")
            self.assertContains(response, "Public Stories")
            self.assertContains(response, "Your Stories")
            self.assertContains(response, user.username.title())

        story = Story.objects.create(title="Awesome story")
        response = self.client.get(
            reverse('display_story', kwargs={'id': story.id})
        )
        response = self.client.get(reverse(page))
        self.assertContains(response, "<div class='menu'>")
        self.assertContains(response, reverse('index'))
        self.assertContains(response, reverse('stories'))
        self.assertContains(response, reverse('personal'))
        self.assertContains(response, reverse('profile'))
        self.assertContains(response, "Home")
        self.assertContains(response, "Public Stories")
        self.assertContains(response, "Your Stories")
        self.assertContains(response, user.username.title())

        response = self.client.get(reverse(
            'reset_password', kwargs={'uidb64': 'NA', 'token': 'set-password'}
        ))
        self.assertContains(response, "<div class='menu'>")
        self.assertContains(response, reverse('index'))
        self.assertContains(response, reverse('stories'))
        self.assertContains(response, reverse('personal'))
        self.assertContains(response, reverse('profile'))
        self.assertContains(response, "Home")
        self.assertContains(response, "Public Stories")
        self.assertContains(response, "Your Stories")
        self.assertContains(response, user.username.title())

        # User logged out menu content
        response = self.client.get(reverse('logout'))
        self.assertContains(response, "<div class='menu'>")
        self.assertContains(response, reverse('index'))
        self.assertContains(response, reverse('stories'))
        self.assertContains(response, reverse('personal'))
        self.assertContains(response, reverse('login'))
        self.assertContains(response, "Home")
        self.assertContains(response, "Public Stories")
        self.assertContains(response, "Your Stories")
        self.assertContains(response, "Log In")

        response = self.client.get(reverse('index'))
        self.assertContains(response, "<div class='menu'>")
        self.assertContains(response, reverse('index'))
        self.assertContains(response, reverse('stories'))
        self.assertContains(response, reverse('personal'))
        self.assertContains(response, reverse('login'))
        self.assertContains(response, "Home")
        self.assertContains(response, "Public Stories")
        self.assertContains(response, "Your Stories")
        self.assertContains(response, "Log In")
