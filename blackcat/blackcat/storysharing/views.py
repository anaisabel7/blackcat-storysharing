from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View
from .models import Story
from .forms import StartStoryForm


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


class StartStoryView(View):
    template_name = 'storysharing/start_story.html'
    context = {}
    form_name = StartStoryForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_name()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_name(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            public = form.cleaned_data['public']
            story = Story.objects.create(
                title=title,
                public=public
            )
            story.writers.set(form.cleaned_data['writers'])
            return HttpResponseRedirect(
                reverse('display_story', kwargs={'id': story.id})
            )

        self.context['errors'] = True
        self.context['form'] = form
        return render(request, self.template_name, self.context)


class DisplayStoryView(View):
    pass
