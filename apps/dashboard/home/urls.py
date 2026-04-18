from django.urls import path

from apps.dashboard.home.views import DashboardHomeView

urlpatterns = [
    path('', DashboardHomeView.as_view(), name='home'),
]
