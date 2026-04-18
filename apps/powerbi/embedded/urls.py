from django.urls import path

from apps.powerbi.embedded.views import EmbeddedReportView, ReportAutocompleteView, ReportGroupDetailView, ReportGroupListView

urlpatterns = [
    # path('', ReportGroupListView.as_view(), name='group-list'),
    
    # path('groups/<slug:slug>/', ReportGroupDetailView.as_view(), name='group-detail'),
    # path('<slug:slug>/', EmbeddedReportView.as_view(), name='report-detail'),


    # path("groups/<slug:slug>/", ReportGroupDetailView.as_view(), name="group-detail"),
    # path("reports/<slug:slug>/", EmbeddedReportView.as_view(), name="report-detail"),


    path('', ReportGroupListView.as_view(), name='group-list'),
    path('autocomplete/', ReportAutocompleteView.as_view(), name='report-autocomplete'),
    path('groups/<slug:slug>/', ReportGroupDetailView.as_view(), name='group-detail'),
    path('reports/<slug:slug>/', EmbeddedReportView.as_view(), name='report-detail'),



]
