from apps.core.common.access import filter_queryset_for_user
from apps.settings.mappings.services import MAPPING_DOMAIN_REGISTRY

# def mapping_overview_metrics(user):
#     total_mapped = 0
#     total_unmapped = 0
#     total_inactive = 0
#     domains = []
#     recent_updates = []

#     for domain_key, config in MAPPING_DOMAIN_REGISTRY.items():
#         has_details = config.get('has_details', False)
#         has_category = config.get('has_category', False)

#         detail_model = config.get('detail_model')
#         mapping_model = config.get('mapping_model')

#         if has_details and detail_model is not None:
#             queryset = filter_queryset_for_user(
#                 detail_model.objects.select_related(
#                     'property',
#                     'mapping',
#                     'mapping__category',
#                     'mapping__category__group',
#                 ),
#                 user,
#             )

#             domain_total = queryset.count()
#             domain_mapped = queryset.filter(mapping__isnull=False).count()
#             domain_unmapped = queryset.filter(mapping__isnull=True).count()
#             domain_inactive = queryset.filter(is_active=False).count()

#             recent_updates.extend(list(queryset.order_by('-updated_at')[:5]))

#         elif mapping_model is not None:
#             queryset = filter_queryset_for_user(
#                 mapping_model.objects.select_related(
#                     *['property', 'category', 'category__group'] if has_category else ['property', 'group']
#                 ),
#                 user,
#             )

#             domain_total = queryset.count()

#             if has_category:
#                 domain_unmapped = queryset.filter(category__isnull=True).count()
#             elif config.get('has_group'):
#                 domain_unmapped = queryset.filter(group__isnull=True).count()
#             else:
#                 domain_unmapped = 0

#             domain_mapped = domain_total - domain_unmapped
#             domain_inactive = queryset.filter(is_active=False).count()

#             recent_updates.extend(list(queryset.order_by('-updated_at')[:5]))
#         else:
#             continue

#         total_mapped += domain_mapped
#         total_unmapped += domain_unmapped
#         total_inactive += domain_inactive

#         domains.append({
#             'slug': domain_key,
#             'key': config.get('key', domain_key),
#             'label': config['label'],
#             'description': config['description'],
#             'color': config.get('color', 'orange'),
#             'icon': config.get('icon'),
#             'image': config.get('image'),
#             'card_border_class': config.get('card_border_class'),
#             'card_ring_class': config.get('card_ring_class'),
#             'top_bar_class': config.get('top_bar_class'),
#             'icon_bg_class': config.get('icon_bg_class'),
#             'icon_text_class': config.get('icon_text_class'),
#             'title_hover_class': config.get('title_hover_class'),
#             'arrow_hover_class': config.get('arrow_hover_class'),
#             'button_class': config.get('button_class'),
#             'button_hover_class': config.get('button_hover_class'),
#             'total': domain_total,
#             'mapped': domain_mapped,
#             'unmapped': domain_unmapped,
#             'inactive': domain_inactive,
#         })

#     recent_updates = sorted(
#         recent_updates,
#         key=lambda obj: obj.updated_at or obj.created_at,
#         reverse=True,
#     )[:5]

#     return {
#         'domains': domains,
#         'total_domains': len(domains),
#         'total_mapped': total_mapped,
#         'total_unmapped': total_unmapped,
#         'total_inactive': total_inactive,
#         'recent_updates': recent_updates,
#     }

def mapping_overview_metrics(user):
    total_mapped = 0
    total_unmapped = 0
    total_inactive = 0
    domains = []
    recent_updates = []

    for domain_key, config in MAPPING_DOMAIN_REGISTRY.items():
        has_details = config.get('has_details', False)
        has_category = config.get('has_category', False)

        detail_model = config.get('detail_model')
        mapping_model = config.get('mapping_model')

        if has_details and detail_model is not None:
            detail_field_names = {field.name for field in detail_model._meta.get_fields()}
            detail_select_related = ['property']

            if 'mapping' in detail_field_names:
                detail_select_related.append('mapping')
                try:
                    relation_model = detail_model._meta.get_field('mapping').related_model
                    relation_field_names = {field.name for field in relation_model._meta.get_fields()}

                    if 'category' in relation_field_names:
                        detail_select_related.append('mapping__category')
                        try:
                            category_model = relation_model._meta.get_field('category').related_model
                            category_field_names = {field.name for field in category_model._meta.get_fields()}

                            if 'group' in category_field_names:
                                detail_select_related.append('mapping__category__group')
                            elif 'mapping' in category_field_names:
                                detail_select_related.extend([
                                    'mapping__category__mapping',
                                    'mapping__category__mapping__category',
                                    'mapping__category__mapping__category__group',
                                ])
                        except Exception:
                            pass

                    elif 'group' in relation_field_names:
                        detail_select_related.append('mapping__group')
                except Exception:
                    pass

            if 'source_system' in detail_field_names:
                detail_select_related.append('source_system')

            if 'origin' in detail_field_names:
                detail_select_related.append('origin')

            queryset = filter_queryset_for_user(
                detail_model.objects.select_related(*detail_select_related),
                user,
            )

            domain_total = queryset.count()
            domain_mapped = queryset.filter(mapping__isnull=False).count() if 'mapping' in detail_field_names else domain_total
            domain_unmapped = queryset.filter(mapping__isnull=True).count() if 'mapping' in detail_field_names else 0
            domain_inactive = queryset.filter(is_active=False).count() if 'is_active' in detail_field_names else 0

            recent_updates.extend(list(queryset.order_by('-updated_at')[:5]))

        elif mapping_model is not None:
            mapping_field_names = {field.name for field in mapping_model._meta.get_fields()}
            mapping_select_related = ['property']

            if 'category' in mapping_field_names:
                mapping_select_related.append('category')
                try:
                    category_model = mapping_model._meta.get_field('category').related_model
                    category_field_names = {field.name for field in category_model._meta.get_fields()}

                    if 'group' in category_field_names:
                        mapping_select_related.append('category__group')
                    elif 'mapping' in category_field_names:
                        mapping_select_related.extend([
                            'category__mapping',
                            'category__mapping__category',
                            'category__mapping__category__group',
                        ])
                except Exception:
                    pass

            elif 'group' in mapping_field_names:
                mapping_select_related.append('group')

            queryset = filter_queryset_for_user(
                mapping_model.objects.select_related(*mapping_select_related),
                user,
            )

            domain_total = queryset.count()

            if has_category and 'category' in mapping_field_names:
                domain_unmapped = queryset.filter(category__isnull=True).count()
            elif config.get('has_group') and 'group' in mapping_field_names:
                domain_unmapped = queryset.filter(group__isnull=True).count()
            else:
                domain_unmapped = 0

            domain_mapped = domain_total - domain_unmapped
            domain_inactive = queryset.filter(is_active=False).count() if 'is_active' in mapping_field_names else 0

            recent_updates.extend(list(queryset.order_by('-updated_at')[:5]))
        else:
            continue

        total_mapped += domain_mapped
        total_unmapped += domain_unmapped
        total_inactive += domain_inactive

        domains.append({
            'slug': domain_key,
            'key': config.get('key', domain_key),
            'label': config['label'],
            'description': config['description'],
            'color': config.get('color', 'orange'),
            'icon': config.get('icon'),
            'image': config.get('image'),
            'card_border_class': config.get('card_border_class'),
            'card_ring_class': config.get('card_ring_class'),
            'top_bar_class': config.get('top_bar_class'),
            'icon_bg_class': config.get('icon_bg_class'),
            'icon_text_class': config.get('icon_text_class'),
            'title_hover_class': config.get('title_hover_class'),
            'arrow_hover_class': config.get('arrow_hover_class'),
            'button_class': config.get('button_class'),
            'button_hover_class': config.get('button_hover_class'),
            'total': domain_total,
            'mapped': domain_mapped,
            'unmapped': domain_unmapped,
            'inactive': domain_inactive,
        })

    recent_updates = sorted(
        recent_updates,
        key=lambda obj: obj.updated_at or obj.created_at,
        reverse=True,
    )[:5]

    return {
        'domains': domains,
        'total_domains': len(domains),
        'total_mapped': total_mapped,
        'total_unmapped': total_unmapped,
        'total_inactive': total_inactive,
        'recent_updates': recent_updates,
    }
