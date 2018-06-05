from django.contrib.auth import logout, login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views import View
from .user_forms import CreateUserForm
from blackcat.storysharing.models import User


@method_decorator(sensitive_post_parameters(), name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class CreateUserView(View):
    form_class = CreateUserForm
    template_name = "user/create_user.html"
    context = {}
    success_url = "/"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        self.context['form'] = form
        if form.is_valid():
            logout(request)
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = User.objects.create(username=username, email=email)
            user.set_password(password)
            user.save()
            login(request, user)
            return HttpResponseRedirect(self.success_url)

        return render(request, self.template_name, self.context)
