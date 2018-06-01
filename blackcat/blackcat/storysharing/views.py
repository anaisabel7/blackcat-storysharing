from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from .models import Story


class StoryListMixin(ListView):
    model = Story


class PublicStoriesView(StoryListMixin):

    def get_queryset(self):
        return Story.objects.filter(public=True)


class PersonalStoriesView(StoryListMixin):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return Story.objects.filter(writers__username__in=[self.request.user])
