from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelForm, HiddenInput, CheckboxInput
from .models import Story, StoryWriter, Snippet


class StartStoryForm(ModelForm):

    class Media:
        css = {
            'all': ('admin/css/widgets.css',)
        }

    class Meta:
        model = Story
        fields = ("title", "writers", "public")
        labels = {
            "public":
                "Set this story as public, available for the world to see"
        }
        widgets = {'writers': FilteredSelectMultiple(
            verbose_name="writers", is_stacked=False
        )}
        help_texts = {
            "writers":
                "(Choose others to play with. You will be included as a writer as well.)"
        }


class StoryWriterActiveForm(ModelForm):

    class Meta:
        model = StoryWriter
        fields = ("story", "active")
        widgets = {
            "story": HiddenInput(),
            "active": CheckboxInput(attrs={'onclick': 'this.form.submit();'})
        }


class CreateSnippetForm(ModelForm):

    class Meta:
        model = Snippet
        fields = ("story", "author", "text")
        labels = {
            "text": "Your text"
        }
        widgets = {
            "story": HiddenInput(),
            "author": HiddenInput()
        }
