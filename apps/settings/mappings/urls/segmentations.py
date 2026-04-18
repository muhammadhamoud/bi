# from django.urls import path

# from apps.settings.mappings.views.segmentations import (
#     SegmentCategoryCreateView,
#     SegmentCategoryInlineGroupUpdateView,
#     SegmentCategoryListView,
#     SegmentCategoryOptionsView,
#     SegmentCategoryUpdateView,
#     SegmentCreateView,
#     SegmentDetailCreateView,
#     SegmentDetailDetailView,
#     SegmentDetailInlineSegmentUpdateView,
#     SegmentDetailListView,
#     SegmentDetailUpdateView,
#     SegmentGroupCreateView,
#     SegmentGroupListView,
#     SegmentGroupOptionsView,
#     SegmentGroupUpdateView,
#     SegmentInlineCategoryUpdateView,
#     SegmentListView,
#     SegmentOptionsView,
#     SegmentUpdateView,
# )

# urlpatterns = [
#     path('', SegmentDetailListView.as_view(), name='segment-detail-list'),
#     path('new/', SegmentDetailCreateView.as_view(), name='segment-detail-create'),
#     path('<int:pk>/', SegmentDetailDetailView.as_view(), name='segment-detail-detail'),
#     path('<int:pk>/edit/', SegmentDetailUpdateView.as_view(), name='segment-detail-update'),
#     path('groups/', SegmentGroupListView.as_view(), name='segment-group-list'),
#     path('groups/new/', SegmentGroupCreateView.as_view(), name='segment-group-create'),
#     path('groups/<int:pk>/edit/', SegmentGroupUpdateView.as_view(), name='segment-group-update'),
#     path('categories/', SegmentCategoryListView.as_view(), name='segment-category-list'),
#     path('categories/new/', SegmentCategoryCreateView.as_view(), name='segment-category-create'),
#     path('categories/<int:pk>/edit/', SegmentCategoryUpdateView.as_view(), name='segment-category-update'),
#     path('segments/', SegmentListView.as_view(), name='segment-list'),
#     path('segments/new/', SegmentCreateView.as_view(), name='segment-create'),
#     path('segments/<int:pk>/edit/', SegmentUpdateView.as_view(), name='segment-update'),

#     path('segments/options/segments/', SegmentOptionsView.as_view(), name='segment-options'),
#     path('segments/options/groups/',SegmentGroupOptionsView.as_view(), name='segment-group-options'),
#     path('segments/options/categories/', SegmentCategoryOptionsView.as_view(), name='segment-category-options'),
    
#     path('segments/<int:pk>/inline/category/', SegmentInlineCategoryUpdateView.as_view(), name='segment-inline-category-update'),
#     path('categories/<int:pk>/inline/group/', SegmentCategoryInlineGroupUpdateView.as_view(), name='segment-category-inline-group-update'),
#     path('<int:pk>/inline/segment/', SegmentDetailInlineSegmentUpdateView.as_view(), name='segment-detail-inline-segment-update'),

# ]
