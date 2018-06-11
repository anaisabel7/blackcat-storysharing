from .forms import StartStoryForm
from .models import Story
from django.contrib.admin.widgets import FilteredSelectMultiple
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
