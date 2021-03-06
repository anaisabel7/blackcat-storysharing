from django.db import models
from django.test import TestCase
from .models import Story, Snippet, User, StoryWriter


class StoryTest(TestCase):

    def test_fields(self):
        expected_fields = {
            'title': models.CharField,
            'writers': models.ManyToManyField,
            'public': models.BooleanField,
            'available': models.BooleanField,
            'shareable': models.BooleanField
        }

        for field in expected_fields:
            self.assertTrue(hasattr(Story, field))
            self.assertTrue(isinstance(
                Story._meta.get_field(field), expected_fields[field]
            ))

        no_fields = len(Story._meta.many_to_many) + len(Story._meta.fields)
        self.assertEqual(no_fields, len(expected_fields) + 1)

        self.assertEqual(Story._meta.get_field('title').max_length, 100)

        self.assertEqual(Story._meta.get_field('writers').related_model, User)
        self.assertTrue(hasattr(Story, 'storywriter_set'))

        self.assertEqual(Story._meta.get_field('public').default, False)

        self.assertEqual(Story._meta.get_field('shareable').default, False)


class SnippetTest(TestCase):

    def test_fields(self):
        expected_fields = {
            'story': models.ForeignKey,
            'author': models.ForeignKey,
            'text': models.TextField,
            'edited': models.BooleanField
        }

        for field in expected_fields:
            self.assertTrue(hasattr(Snippet, field))
            self.assertTrue(isinstance(
                Snippet._meta.get_field(field), expected_fields[field]
            ))

        self.assertEqual(len(Snippet._meta.fields), len(expected_fields) + 1)

        self.assertEqual(Snippet._meta.get_field('story').related_model, Story)
        self.assertEqual(
            Snippet._meta.get_field('story').remote_field.on_delete,
            models.CASCADE
        )

        self.assertEqual(Snippet._meta.get_field('author').related_model, User)
        self.assertEqual(
            Snippet._meta.get_field('author').remote_field.on_delete,
            models.SET_NULL
        )
        self.assertEqual(
            Snippet._meta.get_field('author').null,
            True
        )
        self.assertEqual(
            Snippet._meta.get_field('author').blank,
            False
        )

        self.assertEqual(Snippet._meta.get_field('text').max_length, 1000)

        self.assertEqual(Snippet._meta.get_field('edited').default, False)


class StoryWriterTest(TestCase):

    def test_fields(self):
        expected_fields = {
            "story": models.ForeignKey,
            "writer": models.ForeignKey,
            "active": models.BooleanField
        }

        for field in expected_fields:
            self.assertTrue(hasattr(StoryWriter, field))
            self.assertTrue(isinstance(
                StoryWriter._meta.get_field(field),
                expected_fields[field]
            ))

        self.assertEqual(StoryWriter._meta.get_field('active').default, False)

        self.assertEqual(
            StoryWriter._meta.get_field('story').related_model,
            Story
        )
        self.assertEqual(
            StoryWriter._meta.get_field('story').remote_field.on_delete,
            models.CASCADE
        )

        self.assertEqual(
            StoryWriter._meta.get_field('writer').related_model,
            User
        )
        self.assertEqual(
            StoryWriter._meta.get_field('writer').remote_field.on_delete,
            models.CASCADE
        )
