from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin


class BreadcrumbMixin:
    breadcrumbs = []

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('breadcrumbs', self.get_breadcrumbs())
        return context


class AuditFormMixin:
    success_message = ''

    def form_valid(self, form):
        if hasattr(form.instance, 'created_by') and not form.instance.pk:
            form.instance.created_by = self.request.user
        if hasattr(form.instance, 'updated_by'):
            form.instance.updated_by = self.request.user
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response


class ProtectedPageMixin(LoginRequiredMixin):
    login_url = 'login'
