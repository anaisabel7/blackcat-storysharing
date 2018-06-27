from .forms import (
    StartStoryForm, StoryWriterActiveForm, CreateSnippetForm,
    StorySettingsForm
)
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


class StorySettingsFormTest(TestCase):

    def test_meta_content(self):
        self.assertEqual(StorySettingsForm._meta.model, Story)

        self.assertEqual(
            StorySettingsForm._meta.fields,
            ("shareable", "public")
        )

        expected_widgets = {
            "shareable": CheckboxInput,
            "public": CheckboxInput
        }

        for widget in expected_widgets:
            self.assertIn(widget, StorySettingsForm._meta.widgets)
            self.assertTrue(isinstance(
                StorySettingsForm._meta.widgets[widget],
                expected_widgets[widget]
            ))

        self.assertEqual(
            StorySettingsForm._meta.widgets["shareable"].attrs,
            {"onclick": "this.form.submit();"}
        )
        self.assertEqual(
            StorySettingsForm._meta.widgets["public"].attrs,
            {"onclick": "this.form.submit();"}
        )

        expected_labels = {
            "shareable": "Set as shareable",
            "public": "Set as public"
        }

        for label in expected_labels:
            self.assertIn(label, StorySettingsForm._meta.labels)
            self.assertEqual(
                expected_labels[label],
                StorySettingsForm._meta.labels[label]
            )

        expected_help_texts = {
            "shareable": "Everyone who knows (or guesses) the url {}".format(
                "of a shareable story will be able to see its printable page."
            ),
            "public": "A public story will be displayed in our list {}".format(
                "for everyone to read, including the author of each snippet."
            )
        }

        for help_text in expected_help_texts:
            self.assertIn(help_text, StorySettingsForm._meta.help_texts)
            self.assertEqual(
                expected_help_texts[help_text],
                StorySettingsForm._meta.help_texts[help_text]
            )
