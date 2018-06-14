from blackcat.settings import SITE_DOMAIN, EMAIL_HOST_USER
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View
from .models import Story, StoryWriter, Snippet
from .forms import StartStoryForm, StoryWriterActiveForm, CreateSnippetForm


class PublicStoriesView(ListView):
    model = Story
    template_name = 'storysharing/public_stories.html'

    def get_queryset(self):
        return Story.objects.filter(public=True)


class PersonalStoriesView(ListView):
    model = StoryWriter
    template_name = 'storysharing/personal_stories.html'
    form_name = StoryWriterActiveForm

    def set_active_story(self, story):
        no_active_writers = StoryWriter.objects.filter(
            story=story).filter(active=True).count()

        if no_active_writers >= 2:
            story.available = True
        else:
            story.available = False
        story.save()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_name()
        return context

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data(**kwargs)

        form = self.form_name(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            story = form.cleaned_data['story']
            storywriter = StoryWriter.objects.filter(
                story=story
            ).filter(writer=request.user)[0]
            storywriter.active = form.cleaned_data['active']
            storywriter.save()
            self.set_active_story(storywriter.story)

        return self.render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        return StoryWriter.objects.filter(writer=self.request.user)


class StartStoryView(View):
    template_name = 'storysharing/start_story.html'
    context = {}
    form_name = StartStoryForm

    def send_email_to_writers(self, user, story):
        body = "You've been addded to a story created by {}.\n".format(
            user.username) + "If you wish to be part of it, visit {} ".format(
            SITE_DOMAIN + reverse('personal')
            ) + "to manage your list of active stories. {}".format(
            "You can do that anytime.\n\n"
            ) + "As long as you keep the story 'inactive', {}".format(
            "you won't receive emails regarding its progress."
            ) + "You can only take part in the stories you set as active.\n\n"
        body = body + "Kindly, the {} team".format(SITE_DOMAIN)
        for writer in story.writers.get_queryset():
            send_mail(
                "News from Black Cat Story Sharing",
                body,
                EMAIL_HOST_USER,
                [writer.email]
            )

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
            for writer in form.cleaned_data['writers']:
                StoryWriter.objects.create(story=story, writer=writer)
            if request.user not in form.cleaned_data['writers']:
                StoryWriter.objects.create(story=story, writer=request.user)
            self.send_email_to_writers(request.user, story)
            return HttpResponseRedirect(
                reverse('display_story', kwargs={'id': story.id})
            )

        self.context['errors'] = True
        self.context['form'] = form
        return render(request, self.template_name, self.context)


class DisplayStoryView(View):
    template_name = "storysharing/display_story.html"
    form_name = CreateSnippetForm
    context = {}

    def get(self, request, *args, **kwargs):
        try:
            story = Story.objects.filter(id=kwargs['id'])[0]
            self.context['story'] = story
        except IndexError:
            return render(request, self.template_name, {'doesnt_exist': True})

        writers_queryset = story.writers.get_queryset()

        if not (story.public or request.user in writers_queryset):
            return render(request, self.template_name, {'doesnt_exist': True})

        snippets = Snippet.objects.filter(story=story)
        self.context['snippets'] = snippets

        if request.user in writers_queryset:
            self.context['editable'] = True
            storywriter = StoryWriter.objects.filter(
                story=story
            ).filter(writer=request.user)[0]
            self.context['storywriter'] = storywriter

            form = self.form_name()

            last_snippet = snippets.last()

            if last_snippet and last_snippet.author == request.user:
                    form = False

            self.context['form'] = form

        else:
            self.context['editable'] = False

        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):

        form = self.form_name(request.POST)

        story = Story.objects.filter(id=kwargs['id'])[0]

        if form.is_valid():
            snippet_text = form.cleaned_data['text']
            Snippet.objects.create(
                story=story,
                author=request.user,
                text=snippet_text
            )
            form = False

        post_context = {
            "story": story,
            "editable": True,
            "snippets": Snippet.objects.filter(story=story),
            "form": form
        }

        self.context.update(post_context)

        return render(request, self.template_name, self.context)
