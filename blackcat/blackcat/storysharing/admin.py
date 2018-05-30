from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Story, Snippet

admin.site.register(User, UserAdmin)

admin.site.register(Story)
admin.site.register(Snippet)
