from django.urls import path

from apps.usermanagement.users.views import UserCreateView, UserDetailView, UserListView, UserToggleActiveView, UserUpdateView

urlpatterns = [
    path('', UserListView.as_view(), name='list'),
    path('create/', UserCreateView.as_view(), name='create'),
    path('<int:pk>/', UserDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', UserUpdateView.as_view(), name='update'),
    path('<int:pk>/toggle-active/', UserToggleActiveView.as_view(), name='toggle-active'),
]
