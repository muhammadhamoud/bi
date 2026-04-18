from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView

from apps.analytics.kpi.services.dashboard_builders import build_home_dashboard_context
from apps.core.common.mixins import BreadcrumbMixin


class DashboardHomeView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'dashboard/home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_home_dashboard_context(self.request.user, request=self.request))
        context['breadcrumbs'] = [('Dashboard', '')]
        return context
