from collections import defaultdict

from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render

from apps.core.common.access import filter_queryset_for_user, get_accessible_properties
from apps.core.common.mixins import BreadcrumbMixin
from apps.settings.mappings.views.common import DomainViewMixin, MappingAccessMixin
from apps.settings.mappings.models import (
    SegmentGroup,
    SegmentCategory,
    SegmentDetail,
    RateCodeDetail,
)


class DomainHierarchyTreeView(MappingAccessMixin, BreadcrumbMixin, DomainViewMixin, TemplateView):
    template_name = 'settings/mappings/domain_hierarchy_tree.html'

    def render_domain_not_found(self, message, status=404):
        config = self.get_domain()
        return render(
            self.request,
            'errors/inline_404.html',
            {
                'page_title': 'Page not found',
                'message': message,
                'domain': config,
                'domain_slug': self.kwargs.get(self.domain_key_url_kwarg, ''),
                'breadcrumbs': [
                    ('Dashboard', reverse('dashboard:home')),
                    ('Settings', ''),
                    ('Mappings', reverse('settings_mappings:overview')),
                    ('Not found', ''),
                ],
            },
            status=status,
        )

    def dispatch(self, request, *args, **kwargs):
        config = self.get_domain()

        # rate-codes uses segment hierarchy indirectly, so allow the page
        if config.get('key') != 'rate-codes' and not config.get('has_group'):
            return self.render_domain_not_found('This mapping domain does not support hierarchy browsing.')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        domain = self.get_domain()

        context['domain'] = domain
        context['domain_slug'] = self.kwargs.get(self.domain_key_url_kwarg, '')
        context['page_title'] = f"{domain['label']} hierarchy"
        context['properties'] = get_accessible_properties(self.request.user)
        context['breadcrumbs'] = [
            ('Dashboard', reverse('dashboard:home')),
            ('Settings', ''),
            ('Mappings', reverse('settings_mappings:overview')),
            (domain['label'], self.get_root_list_url_with_filters()),
            ('Hierarchy', ''),
        ]
        context['can_manage'] = self.user_can_manage(self.request.user)
        return context

    def user_can_manage(self, user):
        return user.is_superuser or user.has_perm('propertycore.manage_mappings')


class DomainHierarchyTreeDataView(MappingAccessMixin, DomainViewMixin, View):
    def get(self, request, *args, **kwargs):
        domain = self.get_domain()
        property_id = request.GET.get('property_id')
        can_manage = self.user_can_manage(request.user)

        if not property_id:
            return JsonResponse({'results': [], 'can_manage': can_manage})

        if domain.get('key') == 'rate-codes':
            return self.get_rate_code_tree(request, property_id, can_manage)

        group_model = domain.get('group_model')
        category_model = domain.get('category_model')
        mapping_model = domain.get('mapping_model')
        detail_model = domain.get('detail_model')

        has_category = domain.get('has_category', False)
        has_details = domain.get('has_details', False)

        if not group_model or not mapping_model:
            return JsonResponse({'results': [], 'can_manage': can_manage})

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
            mapping_select_related.append('category')
            try:
                category_related_model = mapping_model._meta.get_field('category').related_model
                category_related_fields = {f.name for f in category_related_model._meta.get_fields()}

                if 'group' in category_related_fields:
                    mapping_select_related.append('category__group')
                elif 'mapping' in category_related_fields:
                    mapping_select_related.extend([
                        'category__mapping',
                        'category__mapping__category',
                        'category__mapping__category__group',
                    ])
            except Exception:
                pass
        elif 'group' in mapping_field_names:
            mapping_select_related.append('group')

        mappings_qs = filter_queryset_for_user(
            mapping_model.objects.filter(property_id=property_id, is_active=True).select_related(*mapping_select_related),
            request.user,
        ).order_by(*self.get_ordering_for_model(mapping_model))

        details_qs = None
        if has_details and detail_model:
            detail_select_related = ['property']
            detail_field_names = {f.name for f in detail_model._meta.get_fields()}

            if 'mapping' in detail_field_names:
                detail_select_related.append('mapping')
                try:
                    related_model = detail_model._meta.get_field('mapping').related_model
                    related_fields = {f.name for f in related_model._meta.get_fields()}

                    if 'category' in related_fields:
                        detail_select_related.append('mapping__category')
                        try:
                            category_related_model = related_model._meta.get_field('category').related_model
                            category_related_fields = {f.name for f in category_related_model._meta.get_fields()}

                            if 'group' in category_related_fields:
                                detail_select_related.append('mapping__category__group')
                            elif 'mapping' in category_related_fields:
                                detail_select_related.extend([
                                    'mapping__category__mapping',
                                    'mapping__category__mapping__category',
                                    'mapping__category__mapping__category__group',
                                ])
                        except Exception:
                            pass
                    elif 'group' in related_fields:
                        detail_select_related.append('mapping__group')
                except Exception:
                    pass

            if 'origin' in detail_field_names:
                detail_select_related.append('origin')

            if 'source_system' in detail_field_names:
                detail_select_related.append('source_system')

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
                    'edit_url': reverse(
                        'settings_mappings:detail-update',
                        kwargs={'domain': self.kwargs['domain'], 'pk': detail.id},
                    ) if can_manage else None,
                    'can_manage': can_manage,
                })

        for mapping in mappings_qs:
            count_value = detail_count_by_mapping.get(mapping.id, 0) if has_details else 0

            mapping_node = {
                'id': mapping.id,
                'code': getattr(mapping, 'code', ''),
                'name': getattr(mapping, 'name', ''),
                'count': count_value,
                'detail_room_sum': detail_room_sum_by_mapping.get(mapping.id, 0),
                'children': detail_children.get(mapping.id, []),
                'edit_url': reverse(
                    'settings_mappings:domain-update',
                    kwargs={'domain': self.kwargs['domain'], 'pk': mapping.id},
                ) if can_manage else None,
                'can_manage': can_manage,
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
                    'edit_url': reverse(
                        'settings_mappings:category-update',
                        kwargs={'domain': self.kwargs['domain'], 'pk': category.id},
                    ) if can_manage else None,
                    'can_manage': can_manage,
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
                'edit_url': reverse(
                    'settings_mappings:group-update',
                    kwargs={'domain': self.kwargs['domain'], 'pk': group.id},
                ) if can_manage else None,
                'can_manage': can_manage,
            })

        return JsonResponse({
            'results': results,
            'can_manage': can_manage,
        })

    def get_rate_code_tree(self, request, property_id, can_manage):
        groups_qs = filter_queryset_for_user(
            SegmentGroup.objects.filter(property_id=property_id, is_active=True),
            request.user,
        ).order_by('sort_order', 'name')

        categories_qs = filter_queryset_for_user(
            SegmentCategory.objects.filter(property_id=property_id, is_active=True).select_related('group'),
            request.user,
        ).order_by('group__sort_order', 'sort_order', 'name')

        segment_details_qs = filter_queryset_for_user(
            SegmentDetail.objects.filter(property_id=property_id, is_active=True).select_related(
                'mapping',
                'mapping__category',
                'mapping__category__group',
            ),
            request.user,
        ).order_by(
            'mapping__category__group__sort_order',
            'mapping__category__sort_order',
            'sort_order',
            'name',
        )

        rate_code_details_qs = filter_queryset_for_user(
            RateCodeDetail.objects.filter(property_id=property_id, is_active=True).select_related(
                'mapping',
                'mapping__mapping',
                'mapping__mapping__category',
                'mapping__mapping__category__group',
                'origin',
                'source_system',
            ),
            request.user,
        ).order_by(
            'mapping__mapping__category__group__sort_order',
            'mapping__mapping__category__sort_order',
            'mapping__sort_order',
            'sort_order',
            'name',
        )

        rate_codes_by_segment = defaultdict(list)
        segment_count = defaultdict(int)
        category_count = defaultdict(int)
        group_count = defaultdict(int)

        for detail in rate_code_details_qs:
            segment = detail.mapping
            if not segment:
                continue

            rate_codes_by_segment[segment.id].append({
                'id': detail.id,
                'code': getattr(detail, 'code', ''),
                'name': getattr(detail, 'name', ''),
                'count': 0,
                'edit_url': reverse(
                    'settings_mappings:detail-update',
                    kwargs={'domain': self.kwargs['domain'], 'pk': detail.id},
                ) if can_manage else None,
                'can_manage': can_manage,
            })

            segment_count[segment.id] += 1

            category = getattr(segment, 'category', None)
            if category:
                category_count[category.id] += 1

                group = getattr(category, 'group', None)
                if group:
                    group_count[group.id] += 1

        segment_nodes_by_category = defaultdict(list)
        category_nodes_by_group = defaultdict(list)

        for segment in segment_details_qs:
            category = getattr(segment, 'category', None)
            if not category:
                continue

            segment_nodes_by_category[category.id].append({
                'id': segment.id,
                'code': getattr(segment, 'code', ''),
                'name': getattr(segment, 'name', ''),
                'count': segment_count.get(segment.id, 0),
                'children': rate_codes_by_segment.get(segment.id, []),
                'edit_url': None,
                'can_manage': can_manage,
            })

        for category in categories_qs:
            category_nodes_by_group[category.group_id].append({
                'id': category.id,
                'code': getattr(category, 'code', ''),
                'name': getattr(category, 'name', ''),
                'count': category_count.get(category.id, 0),
                'children': segment_nodes_by_category.get(category.id, []),
                'edit_url': None,
                'can_manage': can_manage,
            })

        results = []
        for group in groups_qs:
            results.append({
                'id': group.id,
                'code': getattr(group, 'code', ''),
                'name': getattr(group, 'name', ''),
                'count': group_count.get(group.id, 0),
                'children': category_nodes_by_group.get(group.id, []),
                'edit_url': reverse(
                    'settings_mappings:group-update',
                    kwargs={'domain': 'segmentations', 'pk': group.id},
                ) if can_manage else None,
                'can_manage': can_manage,
            })

        return JsonResponse({
            'results': results,
            'can_manage': can_manage,
        })

    def user_can_manage(self, user):
        return user.is_superuser or user.has_perm('propertycore.manage_mappings')



# from collections import defaultdict

# from django.http import Http404, JsonResponse
# from django.urls import reverse
# from django.views import View
# from django.views.generic import TemplateView
# from django.shortcuts import render

# from apps.core.common.access import filter_queryset_for_user, get_accessible_properties
# from apps.settings.mappings.views.common import DomainViewMixin, MappingAccessMixin
# from apps.core.common.mixins import BreadcrumbMixin


# class DomainHierarchyTreeView(MappingAccessMixin, BreadcrumbMixin, DomainViewMixin, TemplateView):
#     template_name = 'settings/mappings/domain_hierarchy_tree.html'

#     # def dispatch(self, request, *args, **kwargs):
#     #     config = self.get_domain()
#     #     if not config.get('has_group'):
#     #         raise Http404('This mapping domain does not support hierarchy browsing.')
#     #     return super().dispatch(request, *args, **kwargs)

#     def dispatch(self, request, *args, **kwargs):
#         config = self.get_domain()
#         if not config.get('has_group'):
#             return self.render_domain_not_found('This mapping domain does not support hierarchy browsing.')
#         return super().dispatch(request, *args, **kwargs)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         domain = self.get_domain()
#         context['domain'] = domain
#         context['page_title'] = f"{domain['label']} hierarchy"
#         context['properties'] = get_accessible_properties(self.request.user)
#         context['breadcrumbs'] = [
#             ('Dashboard', reverse('dashboard:home')),
#             ('Settings', ''),
#             ('Mappings', reverse('settings_mappings:overview')),
#             (domain['label'], reverse('settings_mappings:domain-list', kwargs={'domain': self.kwargs['domain']})),
#             ('Hierarchy', ''),
#         ]
#         context['can_manage'] = self.user_can_manage(self.request.user)
#         return context

#     def user_can_manage(self, user):
#         return user.is_superuser or user.has_perm('propertycore.manage_mappings')


# class DomainHierarchyTreeDataView(MappingAccessMixin, DomainViewMixin, View):
#     def get(self, request, *args, **kwargs):
#         domain = self.get_domain()
#         property_id = request.GET.get('property_id')

#         if not property_id:
#             return JsonResponse({'results': [], 'can_manage': self.user_can_manage(request.user)})

#         group_model = domain.get('group_model')
#         category_model = domain.get('category_model')
#         mapping_model = domain.get('mapping_model')
#         detail_model = domain.get('detail_model')

#         has_category = domain.get('has_category', False)
#         has_details = domain.get('has_details', False)
#         can_manage = self.user_can_manage(request.user)

#         if not group_model or not mapping_model:
#             return JsonResponse({'results': [], 'can_manage': can_manage})

#         groups_qs = filter_queryset_for_user(
#             group_model.objects.filter(property_id=property_id, is_active=True),
#             request.user,
#         ).order_by('sort_order', 'name')

#         categories_qs = None
#         if has_category and category_model:
#             categories_qs = filter_queryset_for_user(
#                 category_model.objects.filter(property_id=property_id, is_active=True).select_related('group'),
#                 request.user,
#             ).order_by('group__sort_order', 'sort_order', 'name')

#         mapping_select_related = ['property']
#         mapping_field_names = {f.name for f in mapping_model._meta.get_fields()}
#         if 'category' in mapping_field_names:
#             mapping_select_related.extend(['category', 'category__group'])
#         elif 'group' in mapping_field_names:
#             mapping_select_related.append('group')

#         mappings_qs = filter_queryset_for_user(
#             mapping_model.objects.filter(property_id=property_id, is_active=True).select_related(*mapping_select_related),
#             request.user,
#         ).order_by(*self.get_ordering_for_model(mapping_model))

#         details_qs = None
#         if has_details and detail_model:
#             detail_select_related = ['mapping']
#             detail_field_names = {f.name for f in detail_model._meta.get_fields()}
#             if 'mapping' in detail_field_names:
#                 detail_select_related.extend(['mapping__category', 'mapping__category__group'])

#             details_qs = filter_queryset_for_user(
#                 detail_model.objects.filter(property_id=property_id, is_active=True).select_related(*detail_select_related),
#                 request.user,
#             ).order_by(*self.get_ordering_for_model(detail_model))

#         detail_count_by_group = defaultdict(int)
#         detail_count_by_category = defaultdict(int)
#         detail_count_by_mapping = defaultdict(int)

#         detail_room_sum_by_mapping = defaultdict(int)
#         detail_room_value_by_detail = {}

#         if has_details and details_qs is not None:
#             for detail in details_qs:
#                 mapping = getattr(detail, 'mapping', None)
#                 if not mapping:
#                     continue

#                 detail_count_by_mapping[mapping.id] += 1

#                 if getattr(mapping, 'category_id', None):
#                     detail_count_by_category[mapping.category_id] += 1
#                     category = getattr(mapping, 'category', None)
#                     if category and getattr(category, 'group_id', None):
#                         detail_count_by_group[category.group_id] += 1
#                 elif getattr(mapping, 'group_id', None):
#                     detail_count_by_group[mapping.group_id] += 1

#                 rooms = getattr(detail, 'number_of_rooms', None) or 0
#                 detail_room_sum_by_mapping[mapping.id] += rooms
#                 detail_room_value_by_detail[detail.id] = rooms

#         mapping_children = defaultdict(list)
#         detail_children = defaultdict(list)
#         category_children = defaultdict(list)

#         if has_details and details_qs is not None:
#             for detail in details_qs:
#                 mapping = getattr(detail, 'mapping', None)
#                 if not mapping:
#                     continue

#                 detail_children[mapping.id].append({
#                     'id': detail.id,
#                     'code': getattr(detail, 'code', ''),
#                     'name': getattr(detail, 'name', ''),
#                     'count': detail_room_value_by_detail.get(detail.id, 0),
#                     'edit_url': reverse('settings_mappings:detail-update', kwargs={'domain': self.kwargs['domain'], 'pk': detail.id}) if can_manage else None,
#                     'can_manage': can_manage,
#                 })

#         for mapping in mappings_qs:
#             if has_details:
#                 count_value = detail_count_by_mapping.get(mapping.id, 0)
#             else:
#                 count_value = 0

#             mapping_node = {
#                 'id': mapping.id,
#                 'code': getattr(mapping, 'code', ''),
#                 'name': getattr(mapping, 'name', ''),
#                 'count': count_value,
#                 'detail_room_sum': detail_room_sum_by_mapping.get(mapping.id, 0),
#                 'children': detail_children.get(mapping.id, []),
#                 'edit_url': reverse('settings_mappings:domain-update', kwargs={'domain': self.kwargs['domain'], 'pk': mapping.id}) if can_manage else None,
#                 'can_manage': can_manage,
#             }

#             if has_category and getattr(mapping, 'category_id', None):
#                 category_children[mapping.category_id].append(mapping_node)
#             elif getattr(mapping, 'group_id', None):
#                 mapping_children[mapping.group_id].append(mapping_node)

#         if has_category and categories_qs is not None:
#             for category in categories_qs:
#                 category_node = {
#                     'id': category.id,
#                     'code': getattr(category, 'code', ''),
#                     'name': getattr(category, 'name', ''),
#                     'count': detail_count_by_category.get(category.id, 0) if has_details else len(category_children.get(category.id, [])),
#                     'children': category_children.get(category.id, []),
#                     'edit_url': reverse('settings_mappings:category-update', kwargs={'domain': self.kwargs['domain'], 'pk': category.id}) if can_manage else None,
#                     'can_manage': can_manage,
#                 }
#                 category_children[('group', category.group_id)].append(category_node)

#         results = []
#         for group in groups_qs:
#             if has_category:
#                 children = category_children.get(('group', group.id), [])
#                 count_value = detail_count_by_group.get(group.id, 0) if has_details else len(children)
#             else:
#                 children = mapping_children.get(group.id, [])
#                 count_value = detail_count_by_group.get(group.id, 0) if has_details else len(children)

#             results.append({
#                 'id': group.id,
#                 'code': getattr(group, 'code', ''),
#                 'name': getattr(group, 'name', ''),
#                 'count': count_value,
#                 'children': children,
#                 'edit_url': reverse('settings_mappings:group-update', kwargs={'domain': self.kwargs['domain'], 'pk': group.id}) if can_manage else None,
#                 'can_manage': can_manage,
#             })

#         return JsonResponse({
#             'results': results,
#             'can_manage': can_manage,
#         })

#     def user_can_manage(self, user):
#         return user.is_superuser or user.has_perm('propertycore.manage_mappings')


