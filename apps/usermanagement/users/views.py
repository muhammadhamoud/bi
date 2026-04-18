from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.core.common.access import can_manage_users
from apps.core.common.mixins import AuditFormMixin, BreadcrumbMixin
from apps.usermanagement.users.forms import TailwindAuthenticationForm, UserCreateForm, UserFilterForm, UserUpdateForm
from apps.usermanagement.users.selectors import get_manageable_users


class AuthLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = TailwindAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if not form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)
        return response


class UserAccessRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not can_manage_users(request.user):
            return HttpResponseForbidden('You do not have permission to manage users.')
        return super().dispatch(request, *args, **kwargs)


class UserListView(UserAccessRequiredMixin, BreadcrumbMixin, ListView):
    template_name = 'users/list.html'
    context_object_name = 'users'
    paginate_by = 25

    def get_queryset(self):
        queryset = get_manageable_users(self.request.user)
        self.filter_form = UserFilterForm(self.request.GET or None, actor=self.request.user)
        if self.filter_form.is_valid():
            q = self.filter_form.cleaned_data.get('q')
            role = self.filter_form.cleaned_data.get('role')
            property_obj = self.filter_form.cleaned_data.get('property')
            status = self.filter_form.cleaned_data.get('status')
            if q:
                queryset = queryset.filter(email__icontains=q) | queryset.filter(first_name__icontains=q) | queryset.filter(last_name__icontains=q) | queryset.filter(username__icontains=q)
            if role:
                queryset = queryset.filter(groups__name=role)
            if property_obj:
                queryset = queryset.filter(property_assignments__property=property_obj)
            if status == 'active':
                queryset = queryset.filter(is_active=True)
            elif status == 'inactive':
                queryset = queryset.filter(is_active=False)
        return queryset.distinct().order_by('email')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = getattr(self, 'filter_form', UserFilterForm(actor=self.request.user))
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('Users', '')]
        return context


class UserDetailView(UserAccessRequiredMixin, BreadcrumbMixin, DetailView):
    template_name = 'users/detail.html'
    context_object_name = 'managed_user'

    def get_queryset(self):
        return get_manageable_users(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [
            ('Dashboard', reverse('dashboard:home')),
            ('Users', reverse('users:list')),
            (self.object.name_or_email, ''),
        ]
        return context


class UserCreateView(UserAccessRequiredMixin, AuditFormMixin, BreadcrumbMixin, CreateView):
    template_name = 'users/form.html'
    form_class = UserCreateForm
    success_url = reverse_lazy('users:list')
    success_message = 'User created successfully.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['actor'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create user'
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('Users', reverse('users:list')), ('Create', '')]
        return context


class UserUpdateView(UserAccessRequiredMixin, AuditFormMixin, BreadcrumbMixin, UpdateView):
    template_name = 'users/form.html'
    form_class = UserUpdateForm
    success_message = 'User updated successfully.'

    def get_queryset(self):
        return get_manageable_users(self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['actor'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse('users:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit {self.object.name_or_email}'
        context['breadcrumbs'] = [
            ('Dashboard', reverse('dashboard:home')),
            ('Users', reverse('users:list')),
            (self.object.name_or_email, reverse('users:detail', kwargs={'pk': self.object.pk})),
            ('Edit', ''),
        ]
        return context


class UserToggleActiveView(UserAccessRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(get_manageable_users(request.user), pk=kwargs['pk'])
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        messages.success(request, f'User {"activated" if user.is_active else "deactivated"}.')
        return redirect('users:detail', pk=user.pk)
