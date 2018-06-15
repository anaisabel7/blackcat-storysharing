from .forms import StartStoryForm, StoryWriterActiveForm, CreateSnippetForm
from .models import Story, StoryWriter, Snippet
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import HiddenInput, CheckboxInput
from django.test import TestCase


class StartStoryFormTest(TestCase):

    def test_meta_content(self):

        self.assertEqual(StartStoryForm._meta.model, Story)
        self.assertEqual(
            StartStoryForm._meta.fields,
            ("title", "writers", "public")
        )
        self.assertIn('writers', StartStoryForm._meta.widgets)
        self.assertTrue(isinstance(
            StartStoryForm._meta.widgets['writers'],
            FilteredSelectMultiple
        ))
        self.assertIn('public', StartStoryForm._meta.labels)
        self.assertEqual(
            StartStoryForm._meta.labels['public'],
            "Set this story as public, available for the world to see"
        )

    def test_media_content(self):

        self.assertEqual(
            StartStoryForm().media._css,
            {'all': ['admin/css/widgets.css']}
        )


class StoryWriterActiveFormTest(TestCase):

    def test_meta_content(self):

        self.assertEqual(StoryWriterActiveForm._meta.model, StoryWriter)

        self.assertEqual(
            StoryWriterActiveForm._meta.fields,
            ("story", "active")
        )
        expected_widgets = {
            "story": HiddenInput,
            "active": CheckboxInput
        }
        for widget in expected_widgets:
            self.assertIn(widget, StoryWriterActiveForm._meta.widgets)
            self.assertTrue(isinstance(
                StoryWriterActiveForm._meta.widgets[widget],
                expected_widgets[widget]
            ))

        self.assertEqual(
            StoryWriterActiveForm._meta.widgets['active'].attrs,
            {'onclick': 'this.form.submit();'}
        )


class CreateSnippetFormTest(TestCase):

    def test_meta_content(self):
        self.assertEqual(CreateSnippetForm._meta.model, Snippet)

        self.assertEqual(
            CreateSnippetForm._meta.fields,
            ("story", "author", "text")
        )

        expected_widgets = {
            "story": HiddenInput,
            "author": HiddenInput
        }

        for widget in expected_widgets:
            self.assertIn(widget, CreateSnippetForm._meta.widgets)
            self.assertTrue(isinstance(
                CreateSnippetForm._meta.widgets[widget],
                expected_widgets[widget]
            ))

        self.assertIn("text", CreateSnippetForm._meta.labels)
        self.assertEqual(
            CreateSnippetForm._meta.labels['text'],
            "Your text"
        )
