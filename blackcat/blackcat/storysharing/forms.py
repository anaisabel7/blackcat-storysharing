from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelForm
from .models import Story


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
