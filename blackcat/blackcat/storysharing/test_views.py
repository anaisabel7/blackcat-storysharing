from blackcat.settings import SITE_DOMAIN, EMAIL_HOST_USER
from django.contrib.auth import login
from django.urls import reverse
from django.test import TestCase
from unittest.mock import patch, call
from .models import User, Story, StoryWriter, Snippet
from .urls import urlpatterns
from . import views


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
        StoryWriter.objects.create(story=story, writer=user)
        private_story_response = self.client.get(reverse('stories'))
        self.assertEqual(
            str(response.content),
            str(private_story_response.content)
        )

    def test_content_with_public_stories(self):
        response = self.client.get(reverse('stories'))
        story = Story.objects.create(title="Wonderful Story", public=True)
        user = create_random_user()
        StoryWriter.objects.create(story=story, writer=user)
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

    def create_two_stories_first_active(self):
        user = create_random_user()
        self.client.login(username=user.username, password='password')
        story = Story.objects.create(title="First story by my user")
        StoryWriter.objects.create(story=story, writer=user, active=True)
        other_story = Story.objects.create(title="Second story my user wrote")
        StoryWriter.objects.create(story=other_story, writer=user)
        return user, story, other_story

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse('personal'))
        self.assertRedirects(
            response, reverse('login') + '?next=' + reverse('personal')
        )

    def test_displaying_stories_writen_by_user_only(self):
        user = create_random_user()
        self.client.login(username=user.username, password='password')
        story = Story.objects.create(title="A story my user wrote.")
        StoryWriter.objects.create(story=story, writer=user)
        other_user = User.objects.create(
            username='otheruser', email="an@email.com"
        )
        other_story = Story.objects.create(title="Other story")
        StoryWriter.objects.create(story=other_story, writer=other_user)
        response = self.client.get(reverse('personal'))
        self.assertContains(response, "Stories")
        self.assertContains(response, story.title)
        self.assertContains(response, user.username)
        self.assertNotIn(other_user.username, str(response.content))
        self.assertNotIn(other_story.title, str(response.content))

    def display_as_many_StoryWriterActiveForms_as_stories(self):
        self.create_two_stories_first_active()
        response = self.client.get(reverse('personal'))
        content_chunks = str(response.content).split("</form>")
        content_chunks = content_chunks[:-1]
        self.assertEqual(len(content_chunks), 2)
        for chunk in content_chunks:
            self.assertIn("<form method=\"post\"", chunk)
            self.assertIn("<input type=\"hidden\" name=\"story\"", chunk)
            self.assertIn("<input type=\"checkbox\" name=\"active\"", chunk)
            self.assertIn("onclick=\"this.form.submit();\"", chunk)

        self.assertIn("checked/>", content_chunks[0])

    def test_post_valid_form_change_active(self):
        user, story_one, story_two = self.create_two_stories_first_active()
        storywriter = StoryWriter.objects.filter(
            story=story_one).filter(writer=user)[0]
        self.assertEqual(storywriter.active, True)

        post_data = {
            'story': story_one.id,
            'active': False
        }

        response = self.client.post(reverse('personal'), data=post_data)
        storywriter = StoryWriter.objects.filter(
            story__title=story_one.title).filter(writer=user)[0]
        self.assertEqual(storywriter.active, False)

    @patch.object(
        views.EmailActiveWritersMixin, 'send_email_to_active_writers'
    )
    def test_post_valid_form_available_story(
        self, mock_send_email_to_active_writers
    ):
        user, story_one, story_two = self.create_two_stories_first_active()
        storywriter = StoryWriter.objects.filter(
            story=story_one).filter(writer=user)[0]
        storywriter.active = False
        storywriter.save()

        other_user = User.objects.create(
            username="other_user", email="other@mail.com"
        )
        other_user.set_password('password')
        other_user.save()
        StoryWriter.objects.create(story=story_one, writer=other_user)

        self.assertEqual(story_one.available, False)

        post_data = {
            'story': story_one.id,
            'active': True
        }

        response = self.client.post(reverse('personal'), data=post_data)
        no_active_writers = StoryWriter.objects.filter(
            story=story_one).filter(active=True).count()
        self.assertEqual(no_active_writers, 1)
        self.assertEqual(story_one.available, False)
        mock_send_email_to_active_writers.assert_not_called()

        self.client.login(username=other_user.username, password="password")

        response = self.client.post(reverse('personal'), data=post_data)
        no_active_writers = StoryWriter.objects.filter(
            story=story_one).filter(active=True).count()
        self.assertEqual(no_active_writers, 2)
        story = Story.objects.filter(title=story_one.title)[0]
        self.assertEqual(story.available, True)
        mock_send_email_to_active_writers.assert_called_with(
            story=story_one,
            update="The story is now available to play."
        )


class DisplayStoryViewTest(TestCase):

    inactive_user_text = "If you want to play here, visit".format(
        "<a href=\"{}\">".format(reverse('personal')) + "your {}".format(
            "personal stories</a> and set it as active."
        )
    )

    def test_displays_public_story(self):
        user = create_random_user()
        story = Story.objects.create(title="Awesome Rodent", public=True)
        text = "At the beginning, a rodent was born."
        Snippet.objects.create(
            text=text,
            author=user,
            story=story
        )
        response = self.client.get(
            reverse('display_story', kwargs={'id': story.id})
        )
        self.assertContains(response, story.title)
        self.assertContains(response, text)
        self.assertContains(response, user.username)

    def test_displays_public_empty_story(self):
        story = Story.objects.create(title="Awesome Rodent", public=True)
        response = self.client.get(
            reverse('display_story', kwargs={'id': story.id})
        )
        self.assertContains(response, story.title)
        self.assertContains(response, "This story is still empty!")

    def test_displays_non_existent_story(self):
        response = self.client.get(
            reverse('display_story', kwargs={'id': 1000})
        )
        self.assertContains(response, "This story doesn't exist!")
        self.assertContains(
            response, "...or maybe it is not available for the world to see."
        )
        self.assertContains(
            response,
            "If you are one of its writers... Maybe you forgot to log in?"
        )

    def test_displays_private_story(self):
        self.client.logout()
        story = Story.objects.create(title="What? This is private!")
        response = self.client.get(
            reverse('display_story', kwargs={'id': story.id})
        )
        self.assertContains(response, "This story doesn't exist!")
        self.assertContains(
            response, "...or maybe it is not available for the world to see."
        )
        self.assertContains(
            response,
            "If you are one of its writers... Maybe you forgot to log in?"
        )
        self.assertNotIn(story.title, str(response.content))

        user = create_random_user()
        self.client.login(username=user.username, password='password')
        writers_usernames = [x['username'] for x in story.writers.values()]
        self.assertNotIn(user.username, writers_usernames)
        response = self.client.get(
            reverse('display_story', kwargs={'id': story.id})
        )
        self.assertContains(response, "This story doesn't exist!")
        self.assertNotIn(story.title, str(response.content))

    def test_displays_unavailable_story(self):
        user = create_random_user()
        story = Story.objects.create(title="Lost in the forest")
        StoryWriter.objects.create(
            story=story, writer=user, active=True
        )
        self.client.login(username=user.username, password='password')
        response = self.client.get(
            reverse('display_story', kwargs={'id': story.id})
        )
        self.assertContains(response, story.title.title())
        self.assertContains(
            response,
            "This story is unavailable. Our game cannot be played on here yet!"
        )

    def test_displays_inactive_user(self):
        user = create_random_user()
        story = Story.objects.create(title="In the forest", available=True)
        storywriter = StoryWriter.objects.create(story=story, writer=user)
        self.client.login(username=user.username, password='password')
        response = self.client.get(
            reverse('display_story', kwargs={'id': story.id})
        )
        self.assertContains(response, story.title.title())
        self.assertContains(response, self.inactive_user_text)

    def test_display_writer_logged_in_active_available_story(self):
        user = create_random_user()
        story = Story.objects.create(title="Fun Adventures", available=True)
        StoryWriter.objects.create(story=story, writer=user, active=True)
        self.client.login(username=user.username, password='password')

        response = self.client.get(
            reverse('display_story', kwargs={'id': story.id})
        )
        self.assertContains(response, "<form method=\"post\"")
        self.assertContains(response, "Add New Snippet")
        self.assertContains(response, "<textarea")
        self.assertContains(response, "<input type=\"submit\"")

    def test_no_form_shown_for_last_snippet_writer(self):
        user = create_random_user()
        other_user = User.objects.create(
            username="otheruser", email="other@email.com"
        )
        other_user.set_password('password')
        other_user.save()

        story = Story.objects.create(title="Fun Story", available=True)
        StoryWriter.objects.create(story=story, writer=user, active=True)
        StoryWriter.objects.create(story=story, writer=other_user, active=True)

        Snippet.objects.create(
            story=story, author=other_user, text="The story starts with hello"
        )
        Snippet.objects.create(
            story=story, author=user, text="And it continues with lots of fun"
        )

        self.client.login(username=user.username, password='password')
        response = self.client.get(
            reverse('display_story', kwargs={'id': story.id})
        )
        self.assertContains(
            response,
            "Thank you for adding your snippet! Wait for one of the other"
        )
        self.assertNotIn("<form", str(response.content))
        self.assertNotIn("Add New Snippet", str(response.content))

        self.client.login(username=other_user.username, password='password')
        response = self.client.get(
            reverse('display_story', kwargs={'id': story.id})
        )
        self.assertContains(response, "<form method=\"post\"")
        self.assertContains(response, "Add New Snippet")
        self.assertNotIn(
            "Thank you for adding your snippet! Wait for one of the other",
            str(response.content)
        )

    @patch.object(
        views.EmailActiveWritersMixin, 'send_email_to_active_writers'
    )
    def test_post_valid_form(self, mock_send_email_to_active_writers):
        user = create_random_user()
        story = Story.objects.create(title="A scary story", available=True)
        StoryWriter.objects.create(story=story, writer=user, active=True)
        self.client.login(username=user.username, password='password')

        text = "The monster and the dragon were fighting."

        post_data = {
            'text': text,
            'story': story.id,
            'author': user.id
        }

        response = self.client.post(
            reverse('display_story', kwargs={'id': story.id}),
            data=post_data
        )
        story_snippets = Snippet.objects.filter(story=story)
        self.assertEqual(len(story_snippets), 1)
        self.assertEqual(story_snippets[0].text, text)
        self.assertContains(response, text)
        self.assertContains(response, user.username)
        self.assertContains(response, story.title.title())
        self.assertContains(
            response,
            "Thank you for adding your snippet! Wait for one of the other"
        )
        self.assertNotIn("<form", str(response.content))
        mock_send_email_to_active_writers.assert_called_with(
            story=story,
            update="A new Snippet has been added to the story."
        )

    @patch.object(
        views.EmailActiveWritersMixin, 'send_email_to_active_writers'
    )
    def test_post_invalid_form(self, mock_send_email_to_active_writers):
        user = create_random_user()
        story = Story.objects.create(title="A scary story", available=True)
        StoryWriter.objects.create(story=story, writer=user, active=True)
        self.client.login(username=user.username, password='password')

        text = "The monster and the dragon were fighting."

        post_data = {
            'text': text,
            'story': story.title,
            'author': user.id
        }

        response = self.client.post(
            reverse('display_story', kwargs={'id': story.id}),
            data=post_data
        )
        self.assertContains(response, "<form method=\"post\"")
        self.assertContains(
            response,
            "Problems found when trying to add the snippet. You can try again."
        )
        story_snippets = Snippet.objects.filter(story=story)
        self.assertEqual(len(story_snippets), 0)
        mock_send_email_to_active_writers.assert_not_called()


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
        another_user = User.objects.create(
            username="otheruser",
            email='other@email.com'
        )
        post_data = {
            'title': "A story title",
            'writers': [another_user.id],
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
        self.assertEqual(story.writers.count(), 2)
        self.assertIn(user, story.writers.all())
        self.assertIn(another_user, story.writers.all())
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


class EmailActiveWritersMixinTest(TestCase):

    @patch.object(views, 'send_mail')
    def test_email_sent_correctly(self, mock_send_mail):
        user = create_random_user()
        other_user = User.objects.create(
            username="otheruser", email="other@email.com"
        )
        third_user = User.objects.create(
            username="thirduser", email="third@email.com"
        )
        story = Story.objects.create(title="Awesome Story")
        StoryWriter.objects.create(story=story, writer=user, active=True)
        StoryWriter.objects.create(story=story, writer=other_user, active=True)
        StoryWriter.objects.create(story=story, writer=third_user)

        update = "Beautiful Update"
        views.EmailActiveWritersMixin().send_email_to_active_writers(
            story=story,
            update=update
        )
        body = "We've got an update regarding your story \"{}\":\n{}\n".format(
            story.title.title(), update
        ) + "You can visit your story here: {}\n".format(
            SITE_DOMAIN + reverse('display_story', kwargs={'id': story.id})
        ) + "If you don't want to receive updates about this story, {}".format(
            "set it as inactive in your personal stories here: {}\n".format(
                SITE_DOMAIN + reverse('personal')
            )
        ) + "Kindly, the {} team.".format(SITE_DOMAIN)

        all_calls = mock_send_mail.mock_calls
        user_call = call(
            "Black Cat Story Sharing - Update",
            body,
            EMAIL_HOST_USER,
            [user.email]
        )
        other_user_call = call(
            "Black Cat Story Sharing - Update",
            body,
            EMAIL_HOST_USER,
            [other_user.email]
        )
        self.assertIn(user_call, all_calls)
        self.assertIn(other_user_call, all_calls)
        self.assertEqual(len(all_calls), 2)


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
