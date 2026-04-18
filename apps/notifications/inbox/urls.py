from django.urls import path

from apps.notifications.inbox.views import NotificationListView, NotificationMarkAllReadView, NotificationMarkReadView

urlpatterns = [
    path('', NotificationListView.as_view(), name='list'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='mark-read'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='mark-all-read'),
]
