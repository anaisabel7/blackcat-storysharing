from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views import View
from .user_forms import CreateUserForm, ProfileForm
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


@method_decorator(sensitive_post_parameters(), name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
@method_decorator(never_cache, name='dispatch')
@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    form_class = ProfileForm
    template_name = "storysharing/profile.html"
    context = {}

    def get_initial_form(self, request):
        initial = {
            "username": request.user.username,
            'email': request.user.email
        }
        return initial

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.get_initial_form(request))
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=request.user)
        self.context['applied'] = False

        if form.is_valid():
            user = request.user
            user.email = form.cleaned_data['email']
            user.save()
            form = self.form_class(initial=self.get_initial_form(request))
            self.context['applied'] = True

        self.context['submitted'] = True
        self.context['form'] = form
        return render(request, self.template_name, self.context)
