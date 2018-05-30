from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.generic import ListView
from .models import Story


class StoryListView(ListView):
    model = Story

    def get_queryset(self):
        return Story.objects.filter(public=True)
