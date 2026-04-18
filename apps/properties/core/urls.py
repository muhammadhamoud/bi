from django.urls import path

from apps.properties.core.views import SwitchPropertyView, PropertyCreateView

urlpatterns = [
    path('switch/', SwitchPropertyView.as_view(), name='switch'),
    path('properties/new/', PropertyCreateView.as_view(), name='property-create'),
]

