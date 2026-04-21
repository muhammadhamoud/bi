from django.urls import path

from apps.dashboard.home.views import DashboardHomeView

urlpatterns = [
    path('', DashboardHomeView.as_view(), name='home'),

#     path(
#     'guest-countries/quick/',
#     GuestCountryQuickListView.as_view(),
#     name='guest-country-quick-list',
# ),
]
