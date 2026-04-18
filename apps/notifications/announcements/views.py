from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.core.common.access import user_is_admin
from apps.core.common.mixins import AuditFormMixin, BreadcrumbMixin
from apps.notifications.announcements.forms import AnnouncementForm
from apps.notifications.announcements.models import Announcement, AnnouncementAcknowledgement


class AnnouncementListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    template_name = 'announcements/list.html'
    context_object_name = 'announcements'
    paginate_by = 20

    def get_queryset(self):
        queryset = Announcement.objects.select_related('created_by').prefetch_related('properties').order_by('-created_at')
        if user_is_admin(self.request.user):
            return queryset
        queryset = queryset.filter_active(timezone.now())
        return [announcement for announcement in queryset if announcement.is_visible_to_user(self.request.user)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('Announcements', '')]
        context['can_manage'] = user_is_admin(self.request.user)
        return context


class AnnouncementAdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not user_is_admin(request.user):
            return HttpResponseForbidden('Only admins can manage announcements.')
        return super().dispatch(request, *args, **kwargs)


class AnnouncementCreateView(AnnouncementAdminRequiredMixin, AuditFormMixin, BreadcrumbMixin, CreateView):
    template_name = 'announcements/form.html'
    form_class = AnnouncementForm
    success_url = reverse_lazy('announcements:list')
    success_message = 'Announcement published successfully.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['actor'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create announcement'
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('Announcements', reverse('announcements:list')), ('Create', '')]
        return context


class AnnouncementUpdateView(AnnouncementAdminRequiredMixin, AuditFormMixin, BreadcrumbMixin, UpdateView):
    template_name = 'announcements/form.html'
    form_class = AnnouncementForm
    queryset = Announcement.objects.all()
    success_url = reverse_lazy('announcements:list')
    success_message = 'Announcement updated successfully.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['actor'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit {self.object.title}'
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('Announcements', reverse('announcements:list')), ('Edit', '')]
        return context


class AnnouncementDismissView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        announcement = get_object_or_404(Announcement, pk=kwargs['pk'])
        ack, _ = AnnouncementAcknowledgement.objects.get_or_create(announcement=announcement, user=request.user)
        ack.dismissed_at = timezone.now()
        ack.save(update_fields=['dismissed_at'])
        messages.success(request, 'Announcement dismissed.')
        return redirect(request.POST.get('next') or 'announcements:list')
