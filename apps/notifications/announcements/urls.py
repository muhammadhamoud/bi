from django.urls import path

from apps.notifications.announcements.views import AnnouncementCreateView, AnnouncementDismissView, AnnouncementListView, AnnouncementUpdateView

urlpatterns = [
    path('', AnnouncementListView.as_view(), name='list'),
    path('create/', AnnouncementCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', AnnouncementUpdateView.as_view(), name='update'),
    path('<int:pk>/dismiss/', AnnouncementDismissView.as_view(), name='dismiss'),
]
