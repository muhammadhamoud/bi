from django.urls import include, path

from apps.settings.mappings.views.common import (
    DetailBulkMappingUpdateView,
    DomainCategoryCreateView,
    DomainCategoryDeleteView,
    DomainCategoryInlineGroupUpdateView,
    DomainCategoryListView,
    DomainCategoryOptionsView,
    DomainCategoryUpdateView,
    DomainDetailCreateView,
    DomainDetailDetailView,
    DomainDetailInlineMappingUpdateView,
    DomainDetailInlineNameUpdateView,
    DomainDetailListView,
    DomainDetailUpdateView,
    DomainGroupCreateView,
    DomainGroupDeleteView,
    DomainGroupListView,
    DomainGroupOptionsView,
    DomainGroupUpdateView,
    DomainHierarchyOptionsView,
    DomainHierarchyView,
    DomainMappingCreateView,
    DomainMappingDeleteView,
    DomainMappingDetailView,
    DomainMappingInlineCategoryUpdateView,
    DomainMappingListView,
    DomainMappingOptionsView,
    DomainMappingUpdateView,
    MappingOverviewView,
)
from apps.settings.mappings.views.hierarchy import DomainHierarchyTreeDataView, DomainHierarchyTreeView
from apps.settings.mappings.views.bulk_copy import BulkMappingCopyView, MappingCopyView

urlpatterns = [
    path('', MappingOverviewView.as_view(), name='overview'),
    # path('segmentations/', include('apps.settings.mappings.urls.segmentations')),

    path( "copy-between-properties/", BulkMappingCopyView.as_view(), name="mapping_bulk_copy"),
    
    path('<slug:domain>/groups/', DomainGroupListView.as_view(), name='group-list'),
    path('<slug:domain>/groups/new/', DomainGroupCreateView.as_view(), name='group-create'),
    path('<slug:domain>/groups/<int:pk>/edit/', DomainGroupUpdateView.as_view(), name='group-update'),

    path('<slug:domain>/categories/', DomainCategoryListView.as_view(), name='category-list'),
    path('<slug:domain>/categories/new/', DomainCategoryCreateView.as_view(), name='category-create'),
    path('<slug:domain>/categories/<int:pk>/edit/', DomainCategoryUpdateView.as_view(), name='category-update'),

    path('<slug:domain>/details/', DomainDetailListView.as_view(), name='detail-list'),
    path('<slug:domain>/details/new/', DomainDetailCreateView.as_view(), name='detail-create'),
    path('<slug:domain>/details/<int:pk>/', DomainDetailDetailView.as_view(), name='detail-detail'),
    path('<slug:domain>/details/<int:pk>/edit/', DomainDetailUpdateView.as_view(), name='detail-update'),

    path('<slug:domain>/options/groups/', DomainGroupOptionsView.as_view(), name='group-options'),
    path('<slug:domain>/options/categories/', DomainCategoryOptionsView.as_view(), name='category-options'),
    path('<slug:domain>/options/mappings/', DomainMappingOptionsView.as_view(), name='mapping-options'),

    path('<slug:domain>/categories/<int:pk>/inline/group/', DomainCategoryInlineGroupUpdateView.as_view(), name='category-inline-group-update'),
    path('<slug:domain>/<int:pk>/inline/category/', DomainMappingInlineCategoryUpdateView.as_view(), name='mapping-inline-category-update'),
    path('<slug:domain>/details/<int:pk>/inline/mapping/', DomainDetailInlineMappingUpdateView.as_view(), name='detail-inline-mapping-update'),

    path('<str:domain>/detail/<int:pk>/inline-name-update/',DomainDetailInlineNameUpdateView.as_view(),name='detail-inline-name-update'),

    path('<slug:domain>/details/bulk-mapping-update/', DetailBulkMappingUpdateView.as_view(), name='detail-bulk-mapping-update'),

    path('<slug:domain>/hierarchy/', DomainHierarchyView.as_view(), name='domain-hierarchy'),
    path('<slug:domain>/hierarchy/options/', DomainHierarchyOptionsView.as_view(), name='domain-hierarchy-options'),

    path('<slug:domain>/', DomainMappingListView.as_view(), name='domain-list'),
    path('<slug:domain>/new/', DomainMappingCreateView.as_view(), name='domain-create'),
    path('<slug:domain>/<int:pk>/', DomainMappingDetailView.as_view(), name='domain-detail'),
    path('<slug:domain>/<int:pk>/edit/', DomainMappingUpdateView.as_view(), name='domain-update'),

    path('<slug:domain>/hierarchy/tree/', DomainHierarchyTreeView.as_view(), name='domain-hierarchy-tree'),
    path('<slug:domain>/hierarchy/tree/data/', DomainHierarchyTreeDataView.as_view(), name='domain-hierarchy-tree-data'),

    path('<slug:domain>/groups/<int:pk>/delete/', DomainGroupDeleteView.as_view(), name='group-delete'),
    path('<slug:domain>/categories/<int:pk>/delete/', DomainCategoryDeleteView.as_view(), name='category-delete'),
    path('<slug:domain>/<int:pk>/delete/', DomainMappingDeleteView.as_view(), name='domain-delete'),

    path( "<str:domain_key>/property/<uuid:property_id>/copy/", MappingCopyView.as_view(), name="mapping_copy"),    

]


# from django.urls import include, path

# from apps.settings.mappings.views.common import (
#     DomainGroupCreateView,
#     DomainGroupListView,
#     DomainGroupUpdateView,
#     DomainMappingCreateView,
#     DomainMappingDetailView,
#     DomainMappingListView,
#     DomainMappingUpdateView,
#     MappingOverviewView,
# )

# urlpatterns = [
#     path('', MappingOverviewView.as_view(), name='overview'),
#     path('segmentations/', include('apps.settings.mappings.urls.segmentations')),
#     path('<slug:domain>/groups/new/', DomainGroupCreateView.as_view(), name='group-create'),
#     path('<slug:domain>/groups/<int:pk>/edit/', DomainGroupUpdateView.as_view(), name='group-update'),
#     path('<slug:domain>/groups/', DomainGroupListView.as_view(), name='group-list'),
#     path('<slug:domain>/new/', DomainMappingCreateView.as_view(), name='domain-create'),
#     path('<slug:domain>/<int:pk>/edit/', DomainMappingUpdateView.as_view(), name='domain-update'),
#     path('<slug:domain>/<int:pk>/', DomainMappingDetailView.as_view(), name='domain-detail'),
#     path('<slug:domain>/', DomainMappingListView.as_view(), name='domain-list'),
# ]
