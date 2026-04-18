from collections import defaultdict
from urllib.parse import urlencode

from django.core.paginator import InvalidPage

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, IntegerField, Q, Value
from django.db.models.deletion import ProtectedError
from django.db.models.functions import Coalesce
from django.http import (
    Http404,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from apps.core.common.access import (
    can_manage_mappings,
    can_view_mappings,
    filter_queryset_for_user,
)
from apps.core.common.mixins import AuditFormMixin, BreadcrumbMixin
from apps.properties.core.selectors import get_accessible_properties
from apps.settings.mappings.forms.common import GroupFilterForm, MappingFilterForm
from apps.settings.mappings.selectors.common import mapping_overview_metrics
from apps.settings.mappings.services import get_mapping_domain
from apps.settings.mappings.views.exporting import CsvExportMixin
from apps.settings.mappings.services.registry import MAPPING_DOMAIN_REGISTRY


class MappingAccessMixin(LoginRequiredMixin):
    # def dispatch(self, request, *args, **kwargs):
    #     if not can_view_mappings(request.user):
    #         return HttpResponseForbidden('You do not have permission to view mappings.')
    #     return super().dispatch(request, *args, **kwargs)
    login_url = 'login'
    redirect_field_name = 'next'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not can_view_mappings(request.user):
            messages.warning(request, 'You do not have access to that page.')
            return redirect('dashboard:home')

        return super().dispatch(request, *args, **kwargs)


class MappingManageMixin(MappingAccessMixin):
    # def dispatch(self, request, *args, **kwargs):
    #     if not can_manage_mappings(request.user):
    #         return HttpResponseForbidden('You do not have permission to manage mappings.')
    #     return super().dispatch(request, *args, **kwargs)
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not can_manage_mappings(request.user):
            messages.warning(request, 'You do not have permission to manage mappings.')
            return redirect('dashboard:home')

        return super().dispatch(request, *args, **kwargs)

class MappingOverviewView(MappingAccessMixin, BreadcrumbMixin, TemplateView):
    template_name = 'settings/mappings/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(mapping_overview_metrics(self.request.user))
        context['breadcrumbs'] = [
            ('Dashboard', reverse('dashboard:home')),
            ('Settings', ''),
            ('Mappings', ''),
        ]
        return context


class DomainViewMixin:
    domain_key_url_kwarg = 'domain'
    persistent_query_keys = ('q', 'property', 'is_active', 'review_required')

    def get_domain(self):
        domain_key = self.kwargs[self.domain_key_url_kwarg]
        try:
            return get_mapping_domain(domain_key)
        except KeyError as exc:
            raise Http404('Mapping domain not found.') from exc

    def get_persistent_querydict(self):
        querydict = self.request.GET.copy()
        filtered = querydict.__class__(mutable=True)

        for key in self.persistent_query_keys:
            value = querydict.get(key)
            if value not in (None, ''):
                filtered[key] = value

        return filtered

    def get_persistent_querystring(self):
        return self.get_persistent_querydict().urlencode()

    def with_persistent_query(self, url):
        query = self.get_persistent_querystring()
        if not query:
            return url
        separator = '&' if '?' in url else '?'
        return f'{url}{separator}{query}'

    def get_success_url_with_filters(self, url_name, **kwargs):
        url = reverse(url_name, kwargs=kwargs)
        return self.with_persistent_query(url)

    def get_root_list_url(self):
        config = self.get_domain()
        if config.get('has_details') and config.get('detail_model'):
            return reverse('settings_mappings:detail-list', kwargs={'domain': self.kwargs['domain']})
        return reverse('settings_mappings:domain-list', kwargs={'domain': self.kwargs['domain']})

    def get_root_list_url_with_filters(self):
        return self.with_persistent_query(self.get_root_list_url())

    def get_model_class(self):
        config = self.get_domain()
        model = config.get(self.model_key)
        if model is None:
            raise Http404(f'{self.model_key} is not configured for this mapping domain.')
        return model

    def get_model_field_names(self, model):
        return {field.name for field in model._meta.get_fields()}

    def model_has_field(self, model, field_name):
        return field_name in self.get_model_field_names(model)

    def get_base_queryset(self):
        model = self.get_model_class()
        return filter_queryset_for_user(model.objects.all(), self.request.user)

    def get_queryset(self):
        return self.get_base_queryset()

    def get_select_related_fields_for_model(self, model):
        field_names = self.get_model_field_names(model)
        select_related_fields = ['property']

        if 'group' in field_names:
            select_related_fields.append('group')

        if 'category' in field_names:
            select_related_fields.append('category')
            try:
                category_model = model._meta.get_field('category').related_model
                if self.model_has_field(category_model, 'group'):
                    select_related_fields.append('category__group')
            except Exception:
                pass

        if 'mapping' in field_names:
            select_related_fields.append('mapping')
            try:
                mapping_model = model._meta.get_field('mapping').related_model
                mapping_field_names = self.get_model_field_names(mapping_model)

                if 'category' in mapping_field_names:
                    select_related_fields.append('mapping__category')
                    try:
                        category_model = mapping_model._meta.get_field('category').related_model
                        if self.model_has_field(category_model, 'group'):
                            select_related_fields.append('mapping__category__group')
                    except Exception:
                        pass
                elif 'group' in mapping_field_names:
                    select_related_fields.append('mapping__group')
            except Exception:
                pass

        if 'source_system' in field_names:
            select_related_fields.append('source_system')

        return select_related_fields

    def get_enriched_queryset(self):
        model = self.get_model_class()
        return self.get_base_queryset().select_related(*self.get_select_related_fields_for_model(model))

    def get_search_query(self, model, q):
        field_names = self.get_model_field_names(model)
        search_q = Q()

        if 'code' in field_names:
            search_q |= Q(code__icontains=q)
        if 'name' in field_names:
            search_q |= Q(name__icontains=q)
        if 'description' in field_names:
            search_q |= Q(description__icontains=q)

        if 'group' in field_names:
            search_q |= Q(group__code__icontains=q) | Q(group__name__icontains=q)

        if 'category' in field_names:
            search_q |= Q(category__code__icontains=q) | Q(category__name__icontains=q)
            try:
                category_model = model._meta.get_field('category').related_model
                if self.model_has_field(category_model, 'group'):
                    search_q |= Q(category__group__code__icontains=q) | Q(category__group__name__icontains=q)
            except Exception:
                pass

        if 'mapping' in field_names:
            search_q |= Q(mapping__code__icontains=q) | Q(mapping__name__icontains=q)
            try:
                mapping_model = model._meta.get_field('mapping').related_model
                mapping_field_names = self.get_model_field_names(mapping_model)

                if 'category' in mapping_field_names:
                    search_q |= Q(mapping__category__code__icontains=q) | Q(mapping__category__name__icontains=q)
                    try:
                        category_model = mapping_model._meta.get_field('category').related_model
                        if self.model_has_field(category_model, 'group'):
                            search_q |= (
                                Q(mapping__category__group__code__icontains=q) |
                                Q(mapping__category__group__name__icontains=q)
                            )
                    except Exception:
                        pass
                elif 'group' in mapping_field_names:
                    search_q |= Q(mapping__group__code__icontains=q) | Q(mapping__group__name__icontains=q)
            except Exception:
                pass

        return search_q

    def get_ordering_for_model(self, model):
        field_names = self.get_model_field_names(model)
        ordering = ['property__name']

        if 'group' in field_names:
            ordering.extend(['sort_order', 'name'])
            return ordering

        if 'category' in field_names:
            try:
                category_model = model._meta.get_field('category').related_model
                if self.model_has_field(category_model, 'group'):
                    ordering.extend(['category__group__sort_order', 'category__sort_order', 'sort_order', 'name'])
                else:
                    ordering.extend(['category__sort_order', 'sort_order', 'name'])
            except Exception:
                ordering.extend(['sort_order', 'name'])
            return ordering

        if 'mapping' in field_names:
            try:
                mapping_model = model._meta.get_field('mapping').related_model
                mapping_field_names = self.get_model_field_names(mapping_model)

                if 'category' in mapping_field_names:
                    category_model = mapping_model._meta.get_field('category').related_model
                    if self.model_has_field(category_model, 'group'):
                        ordering.extend([
                            'mapping__category__group__sort_order',
                            'mapping__category__sort_order',
                            'mapping__sort_order',
                            'sort_order',
                            'name',
                        ])
                        return ordering
                    ordering.extend([
                        'mapping__category__sort_order',
                        'mapping__sort_order',
                        'sort_order',
                        'name',
                    ])
                    return ordering

                if 'group' in mapping_field_names:
                    ordering.extend([
                        'mapping__group__sort_order',
                        'mapping__sort_order',
                        'sort_order',
                        'name',
                    ])
                    return ordering

                ordering.extend(['mapping__sort_order', 'sort_order', 'name'])
                return ordering
            except Exception:
                ordering.extend(['sort_order', 'name'])
                return ordering

        if 'sort_order' in field_names and 'name' in field_names:
            ordering.extend(['sort_order', 'name'])
        elif 'sort_order' in field_names and 'code' in field_names:
            ordering.extend(['sort_order', 'code'])
        elif 'name' in field_names:
            ordering.append('name')
        elif 'code' in field_names:
            ordering.append('code')

        return ordering

    def get_breadcrumb_label(self):
        return self.get_domain()['label']

    def get_base_breadcrumbs(self):
        return [
            ('Dashboard', reverse('dashboard:home')),
            ('Settings', ''),
            ('Mappings', reverse('settings_mappings:overview')),
            (self.get_breadcrumb_label(), self.get_root_list_url_with_filters()),
        ]

    def add_common_list_context(self, context, filter_form_class):
        config = self.get_domain()
        context['domain'] = config
        context['filter_form'] = getattr(self, 'filter_form', filter_form_class(actor=self.request.user))
        context['can_manage'] = can_manage_mappings(self.request.user)
        context['breadcrumbs'] = self.get_base_breadcrumbs() + [(self.page_title, '')]

        querydict = self.request.GET.copy()
        querydict.pop('page', None)
        context['current_query'] = querydict.urlencode()
        context['persistent_query'] = self.get_persistent_querystring()
        context['root_list_url'] = self.get_root_list_url_with_filters()

        page_obj = context.get('page_obj')
        paginator = context.get('paginator')
        if page_obj and paginator:
            current = page_obj.number
            total = paginator.num_pages
            start = max(current - 2, 1)
            end = min(current + 2, total)
            context['page_range_window'] = range(start, end + 1)

        if config.get('has_group') and config.get('group_model'):
            group_options_by_property = defaultdict(list)
            for obj in filter_queryset_for_user(
                config['group_model'].objects.filter(is_active=True).select_related('property'),
                self.request.user,
            ).order_by('property__name', 'sort_order', 'name'):
                group_options_by_property[obj.property_id].append(obj)
            context['group_options_by_property'] = dict(group_options_by_property)

        if config.get('has_category') and config.get('category_model'):
            category_options_by_property = defaultdict(list)
            category_model = config['category_model']
            category_select_related = ['property']
            if self.model_has_field(category_model, 'group'):
                category_select_related.append('group')

            category_qs = filter_queryset_for_user(
                category_model.objects.filter(is_active=True).select_related(*category_select_related),
                self.request.user,
            ).order_by(*self.get_ordering_for_model(category_model))

            for obj in category_qs:
                category_options_by_property[obj.property_id].append(obj)
            context['category_options_by_property'] = dict(category_options_by_property)

        # if config.get('mapping_model'):
        #     mapping_options_by_property = defaultdict(list)
        #     mapping_qs = filter_queryset_for_user(
        #         config['mapping_model'].objects.filter(is_active=True).select_related(
        #             *self.get_select_related_fields_for_model(config['mapping_model'])
        #         ),
        #         self.request.user,
        #     ).order_by(*self.get_ordering_for_model(config['mapping_model']))

        #     for obj in mapping_qs:
        #         mapping_options_by_property[obj.property_id].append(obj)
        #     context['mapping_options_by_property'] = dict(mapping_options_by_property)

        if config.get('mapping_model'):
            mapping_options_by_property = defaultdict(list)
            mapping_qs = filter_queryset_for_user(
                config['mapping_model'].objects.filter(is_active=True).select_related(
                    *self.get_select_related_fields_for_model(config['mapping_model'])
                ),
                self.request.user,
            ).order_by(*self.get_ordering_for_model(config['mapping_model']))

            for obj in mapping_qs:
                mapping_options_by_property[obj.property_id].append(obj)
            context['mapping_options_by_property'] = dict(mapping_options_by_property)

        if getattr(self, 'current_level', None) == 'detail':
            page_items = context.get('page_obj').object_list if context.get('page_obj') else context.get('object_list', [])
            property_ids = sorted({obj.property_id for obj in page_items if getattr(obj, 'property_id', None)})

            if len(property_ids) == 1:
                property_id = property_ids[0]
                bulk_mapping_qs = mapping_qs.filter(property_id=property_id)

                context['bulk_mapping_enabled'] = True
                context['bulk_mapping_options'] = [
                    {
                        'id': obj.id,
                        'name': getattr(obj, 'name', str(obj)),
                        'category_name': getattr(getattr(obj, 'category', None), 'name', ''),
                    }
                    for obj in bulk_mapping_qs
                ]
            else:
                context['bulk_mapping_enabled'] = False
                context['bulk_mapping_options'] = []

        return context

    def reset_review_required_if_present(self, form):
        if hasattr(form.instance, 'is_review_required'):
            form.instance.is_review_required = False

    def filter_by_standard_filters(self, queryset, cleaned, include_review_required=False):
        if cleaned.get('property'):
            queryset = queryset.filter(property=cleaned['property'])

        if cleaned.get('is_active') == 'active':
            queryset = queryset.filter(is_active=True)
        elif cleaned.get('is_active') == 'inactive':
            queryset = queryset.filter(is_active=False)

        if include_review_required:
            if cleaned.get('review_required') == 'yes':
                queryset = queryset.filter(is_review_required=True)
            elif cleaned.get('review_required') == 'no':
                queryset = queryset.filter(is_review_required=False)

        return queryset


class BaseDomainCreateView(MappingManageMixin, AuditFormMixin, BreadcrumbMixin, DomainViewMixin, CreateView):
    success_message = 'Saved successfully.'
    template_name = 'settings/mappings/domain_form.html'
    page_title = ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['actor'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.reset_review_required_if_present(form)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domain'] = self.get_domain()
        context['page_title'] = self.page_title
        context['can_manage'] = can_manage_mappings(self.request.user)
        context['breadcrumbs'] = self.get_base_breadcrumbs() + [(self.page_title, '')]
        context['current_level'] = getattr(self, 'current_level', None)
        context['root_list_url'] = self.get_root_list_url_with_filters()
        context['persistent_query'] = self.get_persistent_querystring()
        return context


class BaseDomainUpdateView(MappingManageMixin, AuditFormMixin, BreadcrumbMixin, DomainViewMixin, UpdateView):
    success_message = 'Updated successfully.'
    template_name = 'settings/mappings/domain_form.html'
    page_title = ''

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['actor'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.reset_review_required_if_present(form)
        return super().form_valid(form)

    def get_queryset(self):
        return self.get_enriched_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domain'] = self.get_domain()
        context['page_title'] = self.page_title
        context['can_manage'] = can_manage_mappings(self.request.user)
        context['breadcrumbs'] = self.get_base_breadcrumbs() + [(self.page_title, '')]
        context['current_level'] = getattr(self, 'current_level', None)
        context['root_list_url'] = self.get_root_list_url_with_filters()
        context['persistent_query'] = self.get_persistent_querystring()
        return context


class BaseDomainListView(CsvExportMixin, MappingAccessMixin, BreadcrumbMixin, DomainViewMixin, ListView):
    context_object_name = 'objects'
    paginate_by = 30
    filter_form_class = GroupFilterForm
    page_title = ''
    current_level = None

    def get_queryset(self):
        model = self.get_model_class()
        queryset = self.get_enriched_queryset()
        self.filter_form = self.filter_form_class(self.request.GET or None, actor=self.request.user)

        if self.filter_form.is_valid():
            cleaned = self.filter_form.cleaned_data
            q = cleaned.get('q')
            if q:
                queryset = queryset.filter(self.get_search_query(model, q))

            queryset = self.filter_by_standard_filters(
                queryset,
                cleaned,
                include_review_required=(self.filter_form_class is MappingFilterForm),
            )

        return queryset.distinct().order_by(*self.get_ordering_for_model(model))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_common_list_context(context, self.filter_form_class)
        context['current_level'] = self.current_level
        return context

    # def get(self, request, *args, **kwargs):
    #     self.object_list = self.get_queryset()

    #     if self.should_export():
    #         return self.render_to_csv_response(self.object_list)

    #     context = self.get_context_data()
    #     return self.render_to_response(context)

    

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()

        if self.should_export():
            return self.render_to_csv_response(self.object_list)

        try:
            context = self.get_context_data()
            return self.render_to_response(context)
        except InvalidPage:
            querydict = request.GET.copy()
            querydict['page'] = 1
            return redirect(f'{request.path}?{querydict.urlencode()}')
    

    def get_export_filename(self):
        domain = self.get_domain()
        level = self.current_level or 'mapping'
        return f"{domain['key']}_{level}.csv"

    def get_export_headers(self):
        if self.current_level == 'group':
            return [
                ('Property', lambda o: o.property.name),
                ('Code', 'code'),
                ('Name', 'name'),
                ('Description', 'description'),
                ('Sort Order', 'sort_order'),
                ('Active', lambda o: 'Yes' if o.is_active else 'No'),
            ]

        if self.current_level == 'category':
            return [
                ('Property', lambda o: o.property.name),
                ('Code', 'code'),
                ('Name', 'name'),
                ('Group Code', lambda o: getattr(o.group, 'code', '')),
                ('Group Name', lambda o: getattr(o.group, 'name', '')),
                ('Description', 'description'),
                ('Sort Order', 'sort_order'),
                ('Active', lambda o: 'Yes' if o.is_active else 'No'),
            ]

        if self.current_level == 'detail':
            return [
                ('Property', lambda o: o.property.name),
                ('Code', 'code'),
                ('Name', 'name'),
                ('Description', 'description'),
                ('Mapping Code', lambda o: getattr(o.mapping, 'code', '')),
                ('Mapping Name', lambda o: getattr(o.mapping, 'name', '')),
                ('Category Code', lambda o: getattr(getattr(o.mapping, 'category', None), 'code', '')),
                ('Category Name', lambda o: getattr(getattr(o.mapping, 'category', None), 'name', '')),
                ('Group Code', lambda o: getattr(getattr(getattr(o.mapping, 'category', None), 'group', None), 'code', '')),
                ('Group Name', lambda o: getattr(getattr(getattr(o.mapping, 'category', None), 'group', None), 'name', '')),
                ('Source System', lambda o: getattr(o.source_system, 'name', '')),
                ('Notes', 'notes'),
                ('Review Required', lambda o: 'Yes' if o.is_review_required else 'No'),
                ('Effective From', lambda o: o.effective_from or ''),
                ('Effective To', lambda o: o.effective_to or ''),
                ('Sort Order', 'sort_order'),
                ('Active', lambda o: 'Yes' if o.is_active else 'No'),
            ]

        return [
            ('Property', lambda o: o.property.name),
            ('Code', 'code'),
            ('Name', 'name'),
            ('Description', 'description'),
            ('Group Code', lambda o: getattr(getattr(o, 'group', None), 'code', '')),
            ('Group Name', lambda o: getattr(getattr(o, 'group', None), 'name', '')),
            ('Category Code', lambda o: getattr(getattr(o, 'category', None), 'code', '')),
            ('Category Name', lambda o: getattr(getattr(o, 'category', None), 'name', '')),
            ('Sort Order', 'sort_order'),
            ('Source System', lambda o: getattr(getattr(o, 'source_system', None), 'name', '')),
            ('Review Required', lambda o: 'Yes' if getattr(o, 'is_review_required', False) else 'No'),
            ('Active', lambda o: 'Yes' if o.is_active else 'No'),
        ]


class DomainGroupListView(BaseDomainListView):
    template_name = 'settings/mappings/domain_list.html'
    model_key = 'group_model'
    filter_form_class = GroupFilterForm
    page_title = 'Groups'
    current_level = 'group'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_group'):
            raise Http404('This mapping domain does not support groups.')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"{self.get_domain()['label']} groups"
        context['breadcrumbs'] = self.get_base_breadcrumbs() + [('Groups', '')]
        return context


class DomainGroupCreateView(BaseDomainCreateView):
    template_name = 'settings/mappings/domain_form.html'
    model_key = 'group_model'
    current_level = 'group'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_group'):
            raise Http404('This mapping domain does not support groups.')
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return self.get_domain()['group_form']

    def get_success_url(self):
        return self.get_success_url_with_filters(
            'settings_mappings:group-list',
            domain=self.kwargs['domain'],
        )

    @property
    def page_title(self):
        return f"Create {self.get_domain()['label']} group"


class DomainGroupUpdateView(BaseDomainUpdateView):
    template_name = 'settings/mappings/domain_form.html'
    model_key = 'group_model'
    current_level = 'group'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_group'):
            raise Http404('This mapping domain does not support groups.')
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return self.get_domain()['group_form']

    def get_success_url(self):
        return self.get_success_url_with_filters(
            'settings_mappings:group-list',
            domain=self.kwargs['domain'],
        )

    @property
    def page_title(self):
        return f"Edit {self.get_domain()['label']} group"


class DomainCategoryListView(BaseDomainListView):
    template_name = 'settings/mappings/domain_list.html'
    model_key = 'category_model'
    filter_form_class = GroupFilterForm
    page_title = 'Categories'
    current_level = 'category'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_category'):
            raise Http404('This mapping domain does not support categories.')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"{self.get_domain()['label']} categories"
        context['breadcrumbs'] = self.get_base_breadcrumbs() + [('Categories', '')]
        return context


class DomainCategoryCreateView(BaseDomainCreateView):
    template_name = 'settings/mappings/domain_form.html'
    model_key = 'category_model'
    current_level = 'category'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_category'):
            raise Http404('This mapping domain does not support categories.')
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return self.get_domain()['category_form']

    def get_success_url(self):
        return self.get_success_url_with_filters(
            'settings_mappings:category-list',
            domain=self.kwargs['domain'],
        )

    @property
    def page_title(self):
        return f"Create {self.get_domain()['label']} category"


class DomainCategoryUpdateView(BaseDomainUpdateView):
    template_name = 'settings/mappings/domain_form.html'
    model_key = 'category_model'
    current_level = 'category'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_category'):
            raise Http404('This mapping domain does not support categories.')
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return self.get_domain()['category_form']

    def get_success_url(self):
        return self.get_success_url_with_filters(
            'settings_mappings:category-list',
            domain=self.kwargs['domain'],
        )

    @property
    def page_title(self):
        return f"Edit {self.get_domain()['label']} category"


class DomainMappingListView(BaseDomainListView):
    template_name = 'settings/mappings/domain_list.html'
    model_key = 'mapping_model'
    filter_form_class = GroupFilterForm
    current_level = 'mapping'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.get_domain()['label']
        context['breadcrumbs'] = self.get_base_breadcrumbs()[:-1] + [(self.get_domain()['label'], '')]
        return context


class DomainMappingCreateView(BaseDomainCreateView):
    template_name = 'settings/mappings/domain_form.html'
    model_key = 'mapping_model'
    current_level = 'mapping'

    def get_form_class(self):
        return self.get_domain()['mapping_form']

    def get_success_url(self):
        if self.get_domain().get('has_details'):
            return self.get_success_url_with_filters(
                'settings_mappings:detail-list',
                domain=self.kwargs['domain'],
            )
        return self.get_success_url_with_filters(
            'settings_mappings:domain-list',
            domain=self.kwargs['domain'],
        )

    @property
    def page_title(self):
        return f"Create {self.get_domain()['label']}"


class DomainMappingUpdateView(BaseDomainUpdateView):
    template_name = 'settings/mappings/domain_form.html'
    model_key = 'mapping_model'
    current_level = 'mapping'

    def get_form_class(self):
        return self.get_domain()['mapping_form']

    def get_success_url(self):
        return self.get_success_url_with_filters(
            'settings_mappings:domain-detail',
            domain=self.kwargs['domain'],
            pk=self.object.pk,
        )

    @property
    def page_title(self):
        return f"Edit {self.get_domain()['label']}"


class DomainMappingDetailView(MappingAccessMixin, BreadcrumbMixin, DomainViewMixin, DetailView):
    template_name = 'settings/mappings/domain_detail.html'
    context_object_name = 'object'
    model_key = 'mapping_model'
    current_level = 'mapping'

    def get_queryset(self):
        return self.get_enriched_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domain'] = self.get_domain()
        context['can_manage'] = can_manage_mappings(self.request.user)
        context['breadcrumbs'] = self.get_base_breadcrumbs() + [(self.object.code, '')]
        context['current_level'] = self.current_level
        context['persistent_query'] = self.get_persistent_querystring()
        context['root_list_url'] = self.get_root_list_url_with_filters()
        return context


class DomainDetailListView(BaseDomainListView):
    template_name = 'settings/mappings/domain_list.html'
    model_key = 'detail_model'
    filter_form_class = MappingFilterForm
    page_title = 'Details'
    current_level = 'detail'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_details'):
            raise Http404('This mapping domain does not support details.')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"{self.get_domain()['label']} details"
        context['breadcrumbs'] = self.get_base_breadcrumbs()[:-1] + [(f"{self.get_domain()['label']} details", '')]
        return context


class DomainDetailCreateView(BaseDomainCreateView):
    template_name = 'settings/mappings/domain_form.html'
    model_key = 'detail_model'
    current_level = 'detail'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_details'):
            raise Http404('This mapping domain does not support details.')
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return self.get_domain()['detail_form']

    def get_success_url(self):
        return self.get_success_url_with_filters(
            'settings_mappings:detail-list',
            domain=self.kwargs['domain'],
        )

    @property
    def page_title(self):
        return f"Create {self.get_domain()['label']} detail"


class DomainDetailUpdateView(BaseDomainUpdateView):
    template_name = 'settings/mappings/domain_form.html'
    model_key = 'detail_model'
    current_level = 'detail'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_details'):
            raise Http404('This mapping domain does not support details.')
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return self.get_domain()['detail_form']

    def get_success_url(self):
        return self.get_success_url_with_filters(
            'settings_mappings:detail-detail',
            domain=self.kwargs['domain'],
            pk=self.object.pk,
        )

    @property
    def page_title(self):
        return f"Edit {self.get_domain()['label']} detail"


class DomainDetailDetailView(MappingAccessMixin, BreadcrumbMixin, DomainViewMixin, DetailView):
    template_name = 'settings/mappings/domain_detail.html'
    context_object_name = 'object'
    model_key = 'detail_model'
    current_level = 'detail'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_details'):
            raise Http404('This mapping domain does not support details.')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.get_enriched_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domain'] = self.get_domain()
        context['can_manage'] = can_manage_mappings(self.request.user)
        context['current_level'] = self.current_level
        context['breadcrumbs'] = self.get_base_breadcrumbs() + [(self.object.code, '')]
        context['persistent_query'] = self.get_persistent_querystring()
        context['root_list_url'] = self.get_root_list_url_with_filters()
        return context


class BaseDomainInlineUpdateView(MappingManageMixin, DomainViewMixin, View):
    model_key = None
    field_name = None
    related_model_key = None
    partial_template_name = 'settings/mappings/partials/inline_relation_cell.html'
    option_context_name = 'options'
    display_attr = 'name'

    def get_model_class(self):
        return self.get_domain()[self.model_key]

    def get_related_model_class(self):
        return self.get_domain()[self.related_model_key]

    def get_object_queryset(self):
        model = self.get_model_class()
        return filter_queryset_for_user(
            model.objects.select_related(*self.get_select_related_fields_for_model(model)),
            self.request.user,
        )

    def get_related_queryset(self, obj):
        related_model = self.get_related_model_class()
        queryset = filter_queryset_for_user(
            related_model.objects.filter(
                property_id=obj.property_id,
                is_active=True,
            ),
            self.request.user,
        )

        related_field_names = self.get_model_field_names(related_model)
        ordering = ['sort_order']
        if 'name' in related_field_names:
            ordering.append('name')
        elif 'code' in related_field_names:
            ordering.append('code')

        return queryset.order_by(*ordering)

    def get(self, request, *args, **kwargs):
        obj = get_object_or_404(self.get_object_queryset(), pk=kwargs['pk'])
        return self.render_cell(obj)

    def post(self, request, *args, **kwargs):
        obj = get_object_or_404(self.get_object_queryset(), pk=kwargs['pk'])

        value = request.POST.get(self.field_name)
        if not value:
            return HttpResponseBadRequest(f'Missing {self.field_name}.')

        related_obj = get_object_or_404(self.get_related_queryset(obj), pk=value)
        setattr(obj, self.field_name, related_obj)
        obj.save(update_fields=[self.field_name])
        obj.refresh_from_db()

        return self.render_cell(obj)

    def render_cell(self, obj):
        current_related = getattr(obj, self.field_name, None)
        return render(
            self.request,
            self.partial_template_name,
            {
                'object': obj,
                'field_name': self.field_name,
                'display_value': getattr(current_related, self.display_attr, '—'),
                'current_related_id': getattr(current_related, 'pk', None),
                self.option_context_name: self.get_related_queryset(obj),
                'post_url_name': self.request.resolver_match.view_name,
                'domain_key': self.kwargs.get('domain'),
                'domain': self.get_domain(),
            },
        )


class DomainCategoryInlineGroupUpdateView(BaseDomainInlineUpdateView):
    model_key = 'category_model'
    related_model_key = 'group_model'
    field_name = 'group'

    def dispatch(self, request, *args, **kwargs):
        config = self.get_domain()
        if not config.get('has_category') or not config.get('has_group'):
            raise Http404('This mapping domain does not support category/group inline updates.')
        return super().dispatch(request, *args, **kwargs)


class DomainMappingInlineCategoryUpdateView(BaseDomainInlineUpdateView):
    model_key = 'mapping_model'
    related_model_key = 'category_model'
    field_name = 'category'

    def dispatch(self, request, *args, **kwargs):
        config = self.get_domain()
        if not config.get('has_category'):
            raise Http404('This mapping domain does not support mapping/category inline updates.')
        return super().dispatch(request, *args, **kwargs)


class DomainDetailInlineMappingUpdateView(BaseDomainInlineUpdateView):
    model_key = 'detail_model'
    related_model_key = 'mapping_model'
    field_name = 'mapping'

    def dispatch(self, request, *args, **kwargs):
        config = self.get_domain()
        if not config.get('has_details'):
            raise Http404('This mapping domain does not support detail/mapping inline updates.')
        return super().dispatch(request, *args, **kwargs)


class BaseDomainOptionsView(MappingManageMixin, DomainViewMixin, View):
    model_key = None

    def get(self, request, *args, **kwargs):
        property_id = request.GET.get('property_id')
        model = self.get_domain().get(self.model_key)

        if model is None:
            raise Http404('This mapping domain does not support this option type.')

        queryset = filter_queryset_for_user(
            model.objects.filter(is_active=True).select_related(*self.get_select_related_fields_for_model(model)),
            request.user,
        )

        if property_id:
            queryset = queryset.filter(property_id=property_id)
        else:
            queryset = queryset.none()

        return JsonResponse({
            'results': [
                {
                    'id': obj.id,
                    'name': getattr(obj, 'name', str(obj)),
                    'code': getattr(obj, 'code', ''),
                }
                for obj in queryset.order_by(*self.get_ordering_for_model(model))
            ]
        })


class DomainGroupOptionsView(BaseDomainOptionsView):
    model_key = 'group_model'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_group'):
            raise Http404('This mapping domain does not support groups.')
        return super().dispatch(request, *args, **kwargs)


class DomainCategoryOptionsView(BaseDomainOptionsView):
    model_key = 'category_model'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_category'):
            raise Http404('This mapping domain does not support categories.')
        return super().dispatch(request, *args, **kwargs)


class DomainMappingOptionsView(BaseDomainOptionsView):
    model_key = 'mapping_model'


class DomainHierarchyView(MappingAccessMixin, BreadcrumbMixin, DomainViewMixin, TemplateView):
    template_name = 'settings/mappings/domain_hierarchy.html'

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
            (
                domain['label'],
                self.get_success_url_with_filters(
                    'settings_mappings:domain-list',
                    domain=self.kwargs['domain'],
                ),
            ),
            ('Hierarchy', ''),
        ]
        context['persistent_query'] = self.get_persistent_querystring()
        context['root_list_url'] = self.get_root_list_url_with_filters()
        return context


class DomainHierarchyOptionsView(MappingManageMixin, DomainViewMixin, View):
    def get(self, request, *args, **kwargs):
        domain = self.get_domain()
        property_id = request.GET.get('property_id')
        level = request.GET.get('level')
        parent_id = request.GET.get('parent_id')

        if not property_id or not level:
            return JsonResponse({'results': []})

        has_category = domain.get('has_category', False)
        detail_model = domain.get('detail_model')
        has_details = domain.get('has_details', False) and detail_model is not None

        def serialize(qs):
            return [
                {
                    'id': obj.id,
                    'code': getattr(obj, 'code', ''),
                    'name': getattr(obj, 'name', ''),
                    'label': f"{getattr(obj, 'code', '')} - {getattr(obj, 'name', '')}".strip(' -'),
                    'child_count': int(getattr(obj, 'child_count', 0) or 0),
                }
                for obj in qs
            ]

        if level == 'groups':
            model = domain.get('group_model')
            if not model:
                return JsonResponse({'results': []})

            qs = filter_queryset_for_user(
                model.objects.filter(property_id=property_id, is_active=True),
                request.user,
            )

            if has_details:
                if has_category:
                    qs = qs.annotate(
                        child_count=Count(
                            'categories__mappings__details',
                            filter=Q(
                                categories__mappings__details__property_id=property_id,
                                categories__mappings__details__is_active=True,
                            ),
                            distinct=True,
                        )
                    )
                else:
                    qs = qs.annotate(
                        child_count=Count(
                            'mappings__details',
                            filter=Q(
                                mappings__details__property_id=property_id,
                                mappings__details__is_active=True,
                            ),
                            distinct=True,
                        )
                    )
            else:
                qs = qs.annotate(child_count=Count('id') - Count('id'))

            qs = qs.order_by('sort_order', 'name')
            return JsonResponse({'results': serialize(qs)})

        if level == 'categories':
            model = domain.get('category_model')
            if not model or not parent_id:
                return JsonResponse({'results': []})

            qs = filter_queryset_for_user(
                model.objects.filter(property_id=property_id, group_id=parent_id, is_active=True),
                request.user,
            ).select_related('group')

            if has_details:
                qs = qs.annotate(
                    child_count=Count(
                        'mappings__details',
                        filter=Q(
                            mappings__details__property_id=property_id,
                            mappings__details__is_active=True,
                        ),
                        distinct=True,
                    )
                )
            else:
                qs = qs.annotate(child_count=Count('id') - Count('id'))

            qs = qs.order_by('sort_order', 'name')
            return JsonResponse({'results': serialize(qs)})

        if level == 'mappings':
            model = domain.get('mapping_model')
            if not model or not parent_id:
                return JsonResponse({'results': []})

            model_fields = {f.name for f in model._meta.get_fields()}
            filters = {'property_id': property_id, 'is_active': True}

            if 'category' in model_fields:
                filters['category_id'] = parent_id
            elif 'group' in model_fields:
                filters['group_id'] = parent_id
            else:
                return JsonResponse({'results': []})

            qs = filter_queryset_for_user(
                model.objects.filter(**filters),
                request.user,
            )

            if has_details:
                qs = qs.annotate(
                    child_count=Count(
                        'details',
                        filter=Q(
                            details__property_id=property_id,
                            details__is_active=True,
                        ),
                        distinct=True,
                    )
                )
            else:
                qs = qs.annotate(child_count=Count('id') - Count('id'))

            qs = qs.order_by('sort_order', 'name')
            return JsonResponse({'results': serialize(qs)})

        if level == 'details':
            model = domain.get('detail_model')
            if not model or not parent_id:
                return JsonResponse({'results': []})

            filters = {
                'property_id': property_id,
                'is_active': True,
                'mapping_id': parent_id,
            }

            qs = filter_queryset_for_user(
                model.objects.filter(**filters),
                request.user,
            )

            model_fields = {f.name for f in model._meta.get_fields()}

            if 'number_of_rooms' in model_fields:
                qs = qs.annotate(
                    child_count=Coalesce('number_of_rooms', Value(0, output_field=IntegerField()))
                )
            else:
                qs = qs.annotate(
                    child_count=Value(0, output_field=IntegerField())
                )

            qs = qs.order_by('sort_order', 'name')
            return JsonResponse({'results': serialize(qs)})

        return JsonResponse({'results': []})


class BaseDomainDeleteView(MappingManageMixin, BreadcrumbMixin, DomainViewMixin, DeleteView):
    template_name = 'settings/mappings/domain_confirm_delete.html'
    context_object_name = 'object'
    page_title = ''
    current_level = None

    def get_queryset(self):
        return self.get_enriched_queryset()

    def get_success_url(self):
        return self.with_persistent_query(self.root_list_url)

    @property
    def root_list_url(self):
        if self.current_level == 'group':
            return reverse('settings_mappings:group-list', kwargs={'domain': self.kwargs['domain']})
        if self.current_level == 'category':
            return reverse('settings_mappings:category-list', kwargs={'domain': self.kwargs['domain']})
        return reverse('settings_mappings:domain-list', kwargs={'domain': self.kwargs['domain']})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        try:
            self.object.delete()
            messages.success(request, f'{self.get_domain()["label"]} {self.current_level} deleted successfully.')
            return redirect(success_url)
        except ProtectedError:
            messages.error(
                request,
                'This record cannot be deleted because it is linked to other records. Remove dependent items first.'
            )
            return redirect(request.META.get('HTTP_REFERER') or success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['domain'] = self.get_domain()
        context['page_title'] = self.page_title
        context['current_level'] = self.current_level
        context['can_manage'] = can_manage_mappings(self.request.user)
        context['root_list_url'] = self.with_persistent_query(self.root_list_url)
        context['breadcrumbs'] = self.get_base_breadcrumbs() + [(self.page_title, '')]
        context['persistent_query'] = self.get_persistent_querystring()
        return context


class DomainGroupDeleteView(BaseDomainDeleteView):
    model_key = 'group_model'
    current_level = 'group'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_group'):
            raise Http404('This mapping domain does not support groups.')
        return super().dispatch(request, *args, **kwargs)

    @property
    def page_title(self):
        return f'Delete {self.get_domain()["label"]} group'


class DomainCategoryDeleteView(BaseDomainDeleteView):
    model_key = 'category_model'
    current_level = 'category'

    def dispatch(self, request, *args, **kwargs):
        if not self.get_domain().get('has_category'):
            raise Http404('This mapping domain does not support categories.')
        return super().dispatch(request, *args, **kwargs)

    @property
    def page_title(self):
        return f'Delete {self.get_domain()["label"]} category'


class DomainMappingDeleteView(BaseDomainDeleteView):
    model_key = 'mapping_model'
    current_level = 'mapping'

    @property
    def page_title(self):
        return f'Delete {self.get_domain()["label"]}'
    

class DetailBulkMappingUpdateView(MappingManageMixin, View):
    def get_safe_redirect_url(self, request):
        referer = request.META.get('HTTP_REFERER')
        if not referer:
            return reverse('settings_mappings:detail-list', kwargs={'domain': self.kwargs['domain']})

        from urllib.parse import urlparse, parse_qsl, urlencode

        parsed = urlparse(referer)
        query = dict(parse_qsl(parsed.query))
        query.pop('page', None)

        query_string = urlencode(query)
        return f'{parsed.path}?{query_string}' if query_string else parsed.path

    def post(self, request, domain, *args, **kwargs):
        config = MAPPING_DOMAIN_REGISTRY.get(domain)
        if not config or not config.get('has_details'):
            messages.error(request, 'Bulk mapping is not available for this domain.')
            return redirect(self.get_safe_redirect_url(request))

        detail_model = config['detail_model']
        mapping_model = config['mapping_model']

        mapping_id = request.POST.get('mapping_id')
        detail_ids = request.POST.getlist('detail_ids')

        if not mapping_id:
            messages.error(request, 'Select a mapping first.')
            return redirect(self.get_safe_redirect_url(request))

        if not detail_ids:
            messages.error(request, 'Select at least one detail row.')
            return redirect(self.get_safe_redirect_url(request))

        mapping_queryset = filter_queryset_for_user(
            mapping_model.objects.select_related('property', 'category'),
            request.user,
        )
        mapping_obj = get_object_or_404(mapping_queryset, pk=mapping_id)

        detail_queryset = filter_queryset_for_user(
            detail_model.objects.select_related('property', 'mapping'),
            request.user,
        ).filter(pk__in=detail_ids)

        valid_detail_ids = list(
            detail_queryset.filter(property_id=mapping_obj.property_id).values_list('id', flat=True)
        )

        if not valid_detail_ids:
            messages.error(request, 'No selected rows belong to the same property as the chosen mapping.')
            return redirect(self.get_safe_redirect_url(request))

        update_kwargs = {'mapping': mapping_obj}
        detail_field_names = {field.name for field in detail_model._meta.get_fields()}
        if 'is_review_required' in detail_field_names:
            update_kwargs['is_review_required'] = False

        updated_count = detail_model.objects.filter(id__in=valid_detail_ids).update(**update_kwargs)
        skipped_count = len(detail_ids) - updated_count

        if skipped_count > 0:
            messages.warning(
                request,
                f'{updated_count} detail rows mapped to {mapping_obj.name}. '
                f'{skipped_count} rows were skipped because they belong to a different property.'
            )
        else:
            messages.success(request, f'{updated_count} detail rows mapped to {mapping_obj.name}.')

        return redirect(self.get_safe_redirect_url(request))

