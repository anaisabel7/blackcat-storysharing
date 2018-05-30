from django.urls import path
from django.views.generic import TemplateView, ListView
from . import views

urlpatterns = [
    path(
        '',
        TemplateView.as_view(template_name='storysharing/index.html'),
        name='index'
    ),
    path(
        'stories',
        views.StoryListView.as_view(),
        name='stories'
    )
]
