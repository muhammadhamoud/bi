from django.urls import path

from apps.usermanagement.profiles.views import ProfileDetailView, ProfilePasswordChangeView, ProfileUpdateView

urlpatterns = [
    path('', ProfileDetailView.as_view(), name='detail'),
    path('edit/', ProfileUpdateView.as_view(), name='update'),
    path('password/', ProfilePasswordChangeView.as_view(), name='change-password'),
]
