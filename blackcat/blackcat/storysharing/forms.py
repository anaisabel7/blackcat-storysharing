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


class StoryWriterDeleteForm(ModelForm):

    class Meta:
        model = StoryWriter
        fields = ('delete',)
        labels = {
            'delete': "Approve to be deleted"
        }
        widgets = {
            "delete": CheckboxInput(attrs={'onlick': 'this.form.submit();'})
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


class StorySettingsForm(ModelForm):

    class Meta:
        model = Story
        fields = ("shareable", "public", "to_be_deleted")
        widgets = {
            "shareable": CheckboxInput(
                attrs={'onclick': 'this.form.submit();'},
            ),
            "public": CheckboxInput(
                attrs={'onclick': 'this.form.submit();'}
            ),
            "to_be_deleted": CheckboxInput(
                attrs={'onclick': 'this.form.submit();'}
            )
        }
        labels = {
            "shareable": "Set as shareable",
            "public": "Set as public",
            "to_be_deleted": "Set as ready to be deleted"
        }
        help_texts = {
            "shareable": "Everyone who knows (or guesses) the url {}".format(
                "of a shareable story will be able to see its printable page."
            ),
            "public": "A public story will be displayed in our list {}".format(
                "for everyone to read, including the author of each snippet."
            ),
            "to_be_deleted": "All active writers will be emailed {}".format(
                "with a link to confirm that this story should be deleted."
            )
        }


class SnippetEditForm(ModelForm):

    class Meta:
        model = Snippet
        fields = ("text",)
