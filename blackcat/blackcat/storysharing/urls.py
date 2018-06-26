from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.i18n import JavaScriptCatalog
from django.views.generic import TemplateView, ListView
from . import views
from .. import user_views

urlpatterns = [
    path(
        '',
        TemplateView.as_view(template_name='storysharing/index.html'),
        name='index'
    ),
    path(
        'stories',
        views.PublicStoriesView.as_view(),
        name='stories'
    ),
    path(
        'personal',
        views.PersonalStoriesView.as_view(),
        name='personal'
    ),
    path(
        'start_story',
        views.StartStoryView.as_view(),
        name='start_story'
    ),
    path(
        'display_story/<id>/',
        views.DisplayStoryView.as_view(),
        name='display_story'
    ),
    path(
        'printable_story/<slug:pk>/',
        views.PrintableStoryView.as_view(),
        name='printable_story'
    )
]

# Auth

urlpatterns = urlpatterns + [
    path(
        'profile',
        user_views.ProfileView.as_view(),
        name='profile'
    ),
    path(
        'create_user',
        user_views.CreateUserView.as_view(),
        name='create_user'
    ),
    path(
        'login',
        auth_views.LoginView.as_view(
            template_name='user/login.html'
        ),
        name='login'
    ),
    path(
        'logout',
        auth_views.LogoutView.as_view(template_name='user/logout.html'),
        name='logout'
    ),
    path(
        'change_password',
        auth_views.PasswordChangeView.as_view(
            template_name='user/change_password.html',
            success_url='change_password_done'
        ),
        name='change_password'
    ),
    path(
        'change_password_done',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='user/change_password_done.html'
        ),
        name='change_password_done'
    ),
    path(
        'lost_password',
        auth_views.PasswordResetView.as_view(
            template_name='user/lost_password.html',
            success_url='/lost_password_done',
            email_template_name='user/email_reset_password.html'
        ),
        name='lost_password'
    ),
    path(
        'lost_password_done',
        auth_views.PasswordResetDoneView.as_view(
            template_name='user/lost_password_done.html'
        ),
        name='lost_password_done'
    ),
    path(
        'reset_password/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            success_url='/reset_password_done',
            template_name='user/reset_password.html',
        ),
        name='reset_password'
    ),
    path(
        'reset_password_done',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='user/reset_password_done.html'
        ),
        name='reset_password_done'
    )
]

# Url change for django admin javascript

urlpatterns = urlpatterns + [
    path(
        'utils/jsi18n/',
        JavaScriptCatalog.as_view(),
        name='jsi18n'
    )
]
