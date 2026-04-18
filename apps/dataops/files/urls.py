from django.urls import path

from apps.dataops.files.views import DataOpsDashboardView, DownloadedFilesView, FileDetailView, FileDownloadView, FileListView, LoadedFilesView, MissingFilesView

urlpatterns = [
    path('', DataOpsDashboardView.as_view(), name='dashboard'),
    path('files/', FileListView.as_view(), name='file-list'),
    path('missing-files/', MissingFilesView.as_view(), name='missing-files'),
    path('loaded-files/', LoadedFilesView.as_view(), name='loaded-files'),
    path('downloaded-files/', DownloadedFilesView.as_view(), name='downloaded-files'),
    path('files/<int:pk>/', FileDetailView.as_view(), name='file-detail'),
    path('files/<int:pk>/download/', FileDownloadView.as_view(), name='file-download'),
]
