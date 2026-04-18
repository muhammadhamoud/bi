from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView

from apps.core.common.mixins import BreadcrumbMixin
from apps.usermanagement.profiles.forms import ProfilePreferencesForm, SelfProfileForm
from apps.usermanagement.users.forms import TailwindPasswordChangeForm


class ProfileDetailView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('My profile', '')]
        return context


class ProfileUpdateView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'users/profile_form.html'

    def get_profile_instance(self):
        return self.request.user.profile

    def get_user_form(self):
        return SelfProfileForm(self.request.POST or None, instance=self.request.user)

    def get_preferences_form(self):
        return ProfilePreferencesForm(self.request.POST or None, self.request.FILES or None, instance=self.get_profile_instance())

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data(user_form=self.get_user_form(), preferences_form=self.get_preferences_form()))

    def post(self, request, *args, **kwargs):
        user_form = self.get_user_form()
        preferences_form = self.get_preferences_form()
        if user_form.is_valid() and preferences_form.is_valid():
            user_form.save()
            preferences_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profiles:detail')
        return self.render_to_response(self.get_context_data(user_form=user_form, preferences_form=preferences_form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('user_form', self.get_user_form())
        context.setdefault('preferences_form', self.get_preferences_form())
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('My profile', reverse('profiles:detail')), ('Edit profile', '')]
        return context


class ProfilePasswordChangeView(LoginRequiredMixin, BreadcrumbMixin, PasswordChangeView):
    template_name = 'users/change_password.html'
    form_class = TailwindPasswordChangeForm
    success_url = reverse_lazy('profiles:detail')

    def form_valid(self, form):
        messages.success(self.request, 'Password updated successfully.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('My profile', reverse('profiles:detail')), ('Change password', '')]
        return context
