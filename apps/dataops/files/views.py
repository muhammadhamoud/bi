from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from apps.core.common.access import can_download_files, can_view_dataops
from apps.core.common.mixins import BreadcrumbMixin
from apps.core.security.services import log_security_event
from apps.dataops.files.forms import FileFilterForm
from apps.dataops.files.models import FileDownloadHistory, FileRecord
from apps.dataops.files.selectors import accessible_download_history, accessible_file_records
from apps.dataops.files.services import build_dataops_dashboard, export_file_records_csv


class DataOpsAccessMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not can_view_dataops(request.user):
            return HttpResponseForbidden('You do not have permission to view data operations.')
        return super().dispatch(request, *args, **kwargs)


class DataOpsDashboardView(DataOpsAccessMixin, BreadcrumbMixin, TemplateView):
    template_name = 'dataops/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_dataops_dashboard(self.request.user))
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('DataOps', '')]
        return context


class BaseFileListView(DataOpsAccessMixin, BreadcrumbMixin, ListView):
    template_name = 'dataops/file_list.html'
    context_object_name = 'files'
    paginate_by = 25
    page_title = 'Files'
    force_status = None

    def get_filter_form(self):
        return FileFilterForm(self.request.GET or None, user=self.request.user)

    def get_queryset(self):
        queryset = accessible_file_records(self.request.user)
        self.filter_form = self.get_filter_form()
        if self.filter_form.is_valid():
            cleaned = self.filter_form.cleaned_data
            if cleaned.get('q'):
                queryset = queryset.filter(file_name__icontains=cleaned['q'])
            if cleaned.get('property'):
                queryset = queryset.filter(property=cleaned['property'])
            if cleaned.get('source_system'):
                queryset = queryset.filter(source_system=cleaned['source_system'])
            if cleaned.get('file_type'):
                queryset = queryset.filter(file_type__icontains=cleaned['file_type'])
            if cleaned.get('status'):
                queryset = queryset.filter(status=cleaned['status'])
            if cleaned.get('start_date'):
                queryset = queryset.filter(expected_for_date__gte=cleaned['start_date'])
            if cleaned.get('end_date'):
                queryset = queryset.filter(expected_for_date__lte=cleaned['end_date'])
        if self.force_status:
            queryset = queryset.filter(status=self.force_status)
        return queryset.order_by('-created_at')

    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('export') == 'csv' and can_view_dataops(self.request.user):
            return export_file_records_csv(context['files'])
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = getattr(self, 'filter_form', self.get_filter_form())
        context['page_title'] = self.page_title
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('DataOps', reverse('dataops:dashboard')), (self.page_title, '')]
        return context


class FileListView(BaseFileListView):
    page_title = 'All files'


class MissingFilesView(BaseFileListView):
    page_title = 'Missing files'
    force_status = FileRecord.LifecycleStatus.MISSING


class LoadedFilesView(BaseFileListView):
    page_title = 'Loaded files'
    force_status = FileRecord.LifecycleStatus.LOADED


class DownloadedFilesView(DataOpsAccessMixin, BreadcrumbMixin, ListView):
    template_name = 'dataops/download_history_list.html'
    context_object_name = 'download_events'
    paginate_by = 25

    def get_queryset(self):
        return accessible_download_history(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Downloaded files'
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('DataOps', reverse('dataops:dashboard')), ('Downloaded files', '')]
        return context


class FileDetailView(DataOpsAccessMixin, BreadcrumbMixin, DetailView):
    template_name = 'dataops/file_detail.html'
    context_object_name = 'file_record'

    def get_queryset(self):
        return accessible_file_records(self.request.user).prefetch_related('event_logs', 'download_history', 'ingestion_jobs')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('DataOps', reverse('dataops:dashboard')), ('Files', reverse('dataops:file-list')), (self.object.file_name, '')]
        return context


class FileDownloadView(DataOpsAccessMixin, View):
    def get(self, request, *args, **kwargs):
        if not can_download_files(request.user):
            return HttpResponseForbidden('You do not have permission to download files.')
        file_record = get_object_or_404(accessible_file_records(request.user), pk=kwargs['pk'])
        FileDownloadHistory.objects.create(
            file_record=file_record,
            user=request.user,
            property=file_record.property,
            reason='Manual review download',
            source_workflow='dashboard',
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        log_security_event(
            category='dataops',
            event_type='file_downloaded',
            severity='info',
            user=request.user,
            property_obj=file_record.property,
            object_repr=file_record.file_name,
            details={'file_id': file_record.id},
            ip_address=request.META.get('REMOTE_ADDR'),
        )
        content = '\n'.join([
            f'File: {file_record.file_name}',
            f'Property: {file_record.property.name}',
            f'Source system: {file_record.source_system.name}',
            f'Status: {file_record.status}',
            f'Expected date: {file_record.expected_for_date}',
            f'Notes: {file_record.notes}',
        ])
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file_record.file_name}.txt"'
        return response
