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



# # TODO remove this
# from django.views.generic import ListView

# from apps.core.common.access import filter_queryset_for_user
# from apps.core.common.mixins import BreadcrumbMixin
# from apps.settings.mappings.models import GuestCountryDetail


# class GuestCountryQuickListView(BreadcrumbMixin, ListView):
#     template_name = 'dashboard/home/guest_country_quick_list.html'
#     context_object_name = 'countries'
#     paginate_by = 300

#     def get_queryset(self):
#         queryset = filter_queryset_for_user(
#             GuestCountryDetail.objects.select_related(
#                 'property',
#                 'mapping',
#                 'mapping__category',
#                 'mapping__category__group',
#             ),
#             self.request.user,
#         ).filter(is_active=True)

#         property_id = self.request.GET.get('property')
#         q = (self.request.GET.get('q') or '').strip()

#         if property_id:
#             queryset = queryset.filter(property_id=property_id)

#         if q:
#             queryset = queryset.filter(name__icontains=q) | queryset.filter(code__icontains=q)

#         return queryset.order_by('name', 'code')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['page_title'] = 'Guest Countries'
#         context['breadcrumbs'] = [
#             ('Dashboard', '/'),
#             ('Settings', ''),
#             ('Mappings', ''),
#             ('Guest Countries', ''),
#         ]
#         context['selected_property'] = self.request.GET.get('property', '')
#         context['search_query'] = self.request.GET.get('q', '')
#         return context
