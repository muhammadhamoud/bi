


from collections import defaultdict

from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce
from django.http import Http404, JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from apps.core.common.access import filter_queryset_for_user, get_accessible_properties
from apps.settings.mappings.views.common import DomainViewMixin, MappingAccessMixin, MappingManageMixin
from apps.core.common.mixins import BreadcrumbMixin


class DomainHierarchyTreeView(MappingAccessMixin, BreadcrumbMixin, DomainViewMixin, TemplateView):
    template_name = 'settings/mappings/domain_hierarchy_tree.html'

    def dispatch(self, request, *args, **kwargs):
        config = self.get_domain()
        if not config.get('has_group'):
            raise Http404('This mapping domain does not support hierarchy browsing.')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        domain = self.get_domain()
        context['domain'] = domain
        context['page_title'] = f"{domain['label']} hierarchy"
        context['properties'] = get_accessible_properties(self.request.user)
        context['breadcrumbs'] = [
            ('Dashboard', reverse('dashboard:home')),
            ('Settings', ''),
            ('Mappings', reverse('settings_mappings:overview')),
            (domain['label'], reverse('settings_mappings:domain-list', kwargs={'domain': self.kwargs['domain']})),
            ('Hierarchy', ''),
        ]
        return context


class DomainHierarchyTreeDataView(MappingManageMixin, DomainViewMixin, View):
    def get(self, request, *args, **kwargs):
        domain = self.get_domain()
        property_id = request.GET.get('property_id')

        if not property_id:
            return JsonResponse({'results': []})

        group_model = domain.get('group_model')
        category_model = domain.get('category_model')
        mapping_model = domain.get('mapping_model')
        detail_model = domain.get('detail_model')

        has_category = domain.get('has_category', False)
        has_details = domain.get('has_details', False)

        if not group_model or not mapping_model:
            return JsonResponse({'results': []})

        groups_qs = filter_queryset_for_user(
            group_model.objects.filter(property_id=property_id, is_active=True),
            request.user,
        ).order_by('sort_order', 'name')

        categories_qs = None
        if has_category and category_model:
            categories_qs = filter_queryset_for_user(
                category_model.objects.filter(property_id=property_id, is_active=True).select_related('group'),
                request.user,
            ).order_by('group__sort_order', 'sort_order', 'name')

        mapping_select_related = ['property']
        mapping_field_names = {f.name for f in mapping_model._meta.get_fields()}
        if 'category' in mapping_field_names:
            mapping_select_related.extend(['category', 'category__group'])
        elif 'group' in mapping_field_names:
            mapping_select_related.append('group')

        mappings_qs = filter_queryset_for_user(
            mapping_model.objects.filter(property_id=property_id, is_active=True).select_related(*mapping_select_related),
            request.user,
        ).order_by(*self.get_ordering_for_model(mapping_model))

        details_qs = None
        if has_details and detail_model:
            detail_select_related = ['mapping']
            detail_field_names = {f.name for f in detail_model._meta.get_fields()}
            if 'mapping' in detail_field_names:
                detail_select_related.extend(['mapping__category', 'mapping__category__group'])

            details_qs = filter_queryset_for_user(
                detail_model.objects.filter(property_id=property_id, is_active=True).select_related(*detail_select_related),
                request.user,
            ).order_by(*self.get_ordering_for_model(detail_model))

        detail_count_by_group = defaultdict(int)
        detail_count_by_category = defaultdict(int)
        detail_count_by_mapping = defaultdict(int)

        detail_room_sum_by_mapping = defaultdict(int)
        detail_room_value_by_detail = {}

        if has_details and details_qs is not None:
            for detail in details_qs:
                mapping = getattr(detail, 'mapping', None)
                if not mapping:
                    continue

                detail_count_by_mapping[mapping.id] += 1

                if getattr(mapping, 'category_id', None):
                    detail_count_by_category[mapping.category_id] += 1
                    category = getattr(mapping, 'category', None)
                    if category and getattr(category, 'group_id', None):
                        detail_count_by_group[category.group_id] += 1
                elif getattr(mapping, 'group_id', None):
                    detail_count_by_group[mapping.group_id] += 1

                rooms = getattr(detail, 'number_of_rooms', None) or 0
                detail_room_sum_by_mapping[mapping.id] += rooms
                detail_room_value_by_detail[detail.id] = rooms

        mapping_children = defaultdict(list)
        detail_children = defaultdict(list)
        category_children = defaultdict(list)

        if has_details and details_qs is not None:
            for detail in details_qs:
                mapping = getattr(detail, 'mapping', None)
                if not mapping:
                    continue
                detail_children[mapping.id].append({
                    'id': detail.id,
                    'code': getattr(detail, 'code', ''),
                    'name': getattr(detail, 'name', ''),
                    'count': detail_room_value_by_detail.get(detail.id, 0),
                    'edit_url': reverse('settings_mappings:detail-update', kwargs={'domain': self.kwargs['domain'], 'pk': detail.id}),
                })

        for mapping in mappings_qs:
            if has_details:
                count_value = detail_count_by_mapping.get(mapping.id, 0)
            else:
                count_value = 0

            mapping_node = {
                'id': mapping.id,
                'code': getattr(mapping, 'code', ''),
                'name': getattr(mapping, 'name', ''),
                'count': count_value,
                'detail_room_sum': detail_room_sum_by_mapping.get(mapping.id, 0),
                'children': detail_children.get(mapping.id, []),
                'edit_url': reverse('settings_mappings:domain-update', kwargs={'domain': self.kwargs['domain'], 'pk': mapping.id}),
            }

            if has_category and getattr(mapping, 'category_id', None):
                category_children[mapping.category_id].append(mapping_node)
            elif getattr(mapping, 'group_id', None):
                mapping_children[mapping.group_id].append(mapping_node)

        if has_category and categories_qs is not None:
            for category in categories_qs:
                category_node = {
                    'id': category.id,
                    'code': getattr(category, 'code', ''),
                    'name': getattr(category, 'name', ''),
                    'count': detail_count_by_category.get(category.id, 0) if has_details else len(category_children.get(category.id, [])),
                    'children': category_children.get(category.id, []),
                    'edit_url': reverse('settings_mappings:category-update', kwargs={'domain': self.kwargs['domain'], 'pk': category.id}),
                }
                category_children[('group', category.group_id)].append(category_node)

        results = []
        for group in groups_qs:
            if has_category:
                children = category_children.get(('group', group.id), [])
                count_value = detail_count_by_group.get(group.id, 0) if has_details else len(children)
            else:
                children = mapping_children.get(group.id, [])
                count_value = detail_count_by_group.get(group.id, 0) if has_details else len(children)

            results.append({
                'id': group.id,
                'code': getattr(group, 'code', ''),
                'name': getattr(group, 'name', ''),
                'count': count_value,
                'children': children,
                'edit_url': reverse('settings_mappings:group-update', kwargs={'domain': self.kwargs['domain'], 'pk': group.id}),
            })

        return JsonResponse({'results': results})