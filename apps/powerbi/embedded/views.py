from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, TemplateView, View
from django.db.models import Q


from apps.core.common.access import can_view_reports, get_current_property
from apps.core.common.mixins import BreadcrumbMixin
from apps.powerbi.embedded.models import PowerBIReport, ReportGroup, ReportViewAuditLog
from apps.powerbi.embedded.selectors import get_accessible_report_groups, get_accessible_reports
from apps.powerbi.embedded.services import PowerBIEmbedService, PowerBIServiceError


class ReportGroupListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    template_name = 'powerbi/group_list.html'
    context_object_name = 'report_groups'

    def dispatch(self, request, *args, **kwargs):
        if not can_view_reports(request.user):
            # return HttpResponseForbidden('You do not have permission to view reports.')
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = get_accessible_report_groups(self.request.user)
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(name__icontains=q)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('Reports', '')]
        return context


# class ReportGroupDetailView(LoginRequiredMixin, BreadcrumbMixin, DetailView):
#     template_name = 'powerbi/group_detail.html'
#     context_object_name = 'report_group'

#     def get_queryset(self):
#         return get_accessible_report_groups(self.request.user)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['reports'] = get_accessible_reports(self.request.user, group=self.object)
#         context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('Reports', reverse('powerbi:group-list')), (self.object.name, '')]
#         return context


class ReportGroupDetailView(LoginRequiredMixin, BreadcrumbMixin, DetailView):
    template_name = 'powerbi/group_detail.html'
    context_object_name = 'report_group'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return get_accessible_report_groups(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reports'] = get_accessible_reports(self.request.user, group=self.object)
        context['breadcrumbs'] = [
            ('Dashboard', reverse('dashboard:home')),
            ('Reports', reverse('powerbi:group-list')),
            (self.object.name, '')
        ]
        return context


class EmbeddedReportView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    template_name = 'powerbi/report_embed.html'

    def get_report(self):
        report = PowerBIReport.objects.select_related('report_group').filter(slug=self.kwargs['slug']).first()
        if not report or not get_accessible_reports(self.request.user).filter(pk=report.pk).exists():
            raise Http404('Report not found.')
        return report

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = self.get_report()
        property_obj = get_current_property(self.request, self.request.user)
        error_message = ''
        embed_config = None
        try:
            if PowerBIEmbedService.is_configured():
                embed_config = PowerBIEmbedService.build_embed_config(report, user=self.request.user, property_obj=property_obj)
                ReportViewAuditLog.objects.create(
                    report=report,
                    user=self.request.user,
                    property=property_obj,
                    success=True,
                    detail='Embed config generated',
                    ip_address=self.request.META.get('REMOTE_ADDR'),
                    user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:255],
                )
            else:
                error_message = 'Power BI environment variables are not configured yet. Configure the .env file to enable embedding.'
        except PowerBIServiceError as exc:
            error_message = str(exc)
            ReportViewAuditLog.objects.create(
                report=report,
                user=self.request.user,
                property=property_obj,
                success=False,
                detail=str(exc)[:255],
                ip_address=self.request.META.get('REMOTE_ADDR'),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')[:255],
            )

        context.update(
            {
                'report': report,
                'embed_config': embed_config,
                'error_message': error_message,
                'breadcrumbs': [
                    ('Dashboard', reverse('dashboard:home')),
                    ('Reports', reverse('powerbi:group-list')),
                    (report.report_group.name, reverse('powerbi:group-detail', kwargs={'slug': report.report_group.slug})),
                    (report.name, ''),
                ],
            }
        )
        return context



class ReportAutocompleteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if not can_view_reports(request.user):
            return JsonResponse({'results': []}, status=403)

        query = request.GET.get('q', '').strip()
        if not query:
            return JsonResponse({'results': []})

        property_obj = get_current_property(request, request.user)
        if not property_obj:
            return JsonResponse({'results': []})

        reports = (
            get_accessible_reports(request.user)
            .select_related('report_group')
            .filter(
                Q(name__icontains=query) |
                Q(slug__icontains=query) |
                Q(description__icontains=query) |
                Q(report_group__name__icontains=query)
            )
            .order_by('report_group__name', 'name')[:10]
        )

        return JsonResponse(
            {
                'results': [
                    {
                        'name': report.name,
                        'url': reverse('powerbi:report-detail', kwargs={'slug': report.slug}),
                        'group': report.report_group.name if report.report_group else '',
                        'slug': report.slug,
                        'description': report.description or '',
                    }
                    for report in reports
                ]
            }
        )
    

