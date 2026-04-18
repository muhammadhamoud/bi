from django.urls import path

from apps.analytics.kpi.views import DailyOccupancyView, ExecutiveOverviewView, GoalsAchievementView, PropertyPerformanceView, RevenuePerformanceView, metrics

urlpatterns = [
    path('executive/', ExecutiveOverviewView.as_view(), name='executive'),
    path('occupancy/', DailyOccupancyView.as_view(), name='occupancy'),
    path('revenue/', RevenuePerformanceView.as_view(), name='revenue'),
    path('properties/', PropertyPerformanceView.as_view(), name='properties'),
    path('goals/', GoalsAchievementView.as_view(), name='goals'),
    path('metrics/', metrics, name='metrics'),
]
