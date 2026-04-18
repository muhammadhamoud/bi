from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView

from apps.core.common.mixins import BreadcrumbMixin
from apps.notifications.inbox.models import Notification


class NotificationListView(LoginRequiredMixin, BreadcrumbMixin, ListView):
    template_name = 'notifications/inbox_list.html'
    context_object_name = 'notifications'
    paginate_by = 25

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = [('Dashboard', reverse('dashboard:home')), ('Notifications', '')]
        return context


class NotificationMarkReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        notification = get_object_or_404(Notification, recipient=request.user, pk=kwargs['pk'])
        if not notification.read_at:
            notification.read_at = timezone.now()
            notification.save(update_fields=['read_at'])
        return redirect(request.POST.get('next') or 'notifications:list')


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(recipient=request.user, read_at__isnull=True).update(read_at=timezone.now())
        messages.success(request, 'All notifications marked as read.')
        return redirect(request.POST.get('next') or 'notifications:list')
