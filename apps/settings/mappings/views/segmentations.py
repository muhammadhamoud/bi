# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.db.models import Q
# from django.http import HttpResponseForbidden, JsonResponse
# from django.urls import reverse, reverse_lazy
# from django.views import View
# from django.views.generic import CreateView, DetailView, ListView, UpdateView

# from collections import defaultdict

# from apps.core.common.access import can_manage_mappings, can_view_mappings, filter_queryset_for_user
# from apps.core.common.mixins import AuditFormMixin, BreadcrumbMixin
# from apps.settings.mappings.forms.common import GroupFilterForm, MappingFilterForm
# from apps.settings.mappings.forms.common import (
#     SegmentCategoryForm,
#     SegmentDetailForm,
#     SegmentForm,
#     SegmentGroupForm,
# )
# from apps.settings.mappings.models import Segment, SegmentCategory, SegmentDetail, SegmentGroup
# from apps.settings.mappings.views.exporting import CsvExportMixin


# class SegmentationAccessMixin(LoginRequiredMixin):
#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return self.handle_no_permission()
#         if not can_view_mappings(request.user):
#             return HttpResponseForbidden('You do not have permission to view segmentations.')
#         return super().dispatch(request, *args, **kwargs)


# class SegmentationManageMixin(SegmentationAccessMixin):
#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return self.handle_no_permission()
#         if not can_manage_mappings(request.user):
#             return HttpResponseForbidden('You do not have permission to manage segmentations.')
#         return super().dispatch(request, *args, **kwargs)


# class BaseSegmentationCreateView(SegmentationManageMixin, AuditFormMixin, BreadcrumbMixin, CreateView):
#     template_name = 'settings/mappings/segmentations/form.html'
#     success_message = 'Saved successfully.'

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['actor'] = self.request.user
#         return kwargs

#     def form_valid(self, form):
#         if hasattr(form.instance, 'is_review_required'):
#             form.instance.is_review_required = False
#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['page_title'] = self.page_title
#         context['can_manage'] = can_manage_mappings(self.request.user)
#         context['breadcrumbs'] = [
#             ('Dashboard', reverse('dashboard:home')),
#             ('Settings', ''),
#             ('Mappings', reverse('settings_mappings:overview')),
#             ('Market Segmentation', reverse('settings_mappings:segment-detail-list')),
#             (self.page_title, ''),
#         ]
#         return context


# class BaseSegmentationUpdateView(SegmentationManageMixin, AuditFormMixin, BreadcrumbMixin, UpdateView):
#     template_name = 'settings/mappings/segmentations/form.html'
#     success_message = 'Updated successfully.'

#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs['actor'] = self.request.user
#         return kwargs

#     def form_valid(self, form):
#         if hasattr(form.instance, 'is_review_required'):
#             form.instance.is_review_required = False
#         return super().form_valid(form)

#     def get_queryset(self):
#         return filter_queryset_for_user(self.model.objects.all(), self.request.user)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['page_title'] = self.page_title
#         context['can_manage'] = can_manage_mappings(self.request.user)
#         context['breadcrumbs'] = [
#             ('Dashboard', reverse('dashboard:home')),
#             ('Settings', ''),
#             ('Mappings', reverse('settings_mappings:overview')),
#             ('Market Segmentation', reverse('settings_mappings:segment-detail-list')),
#             (self.page_title, ''),
#         ]
#         return context


# class BaseSegmentationListView(CsvExportMixin, SegmentationAccessMixin, BreadcrumbMixin, ListView):
#     template_name = 'settings/mappings/segmentations/list.html'
#     context_object_name = 'objects'
#     paginate_by = 30
#     page_title = ''
#     filter_form_class = GroupFilterForm

#     def get_base_queryset(self):
#         if self.model is SegmentGroup:
#             return SegmentGroup.objects.select_related('property')

#         if self.model is SegmentCategory:
#             return SegmentCategory.objects.select_related('property', 'group')

#         if self.model is Segment:
#             return Segment.objects.select_related('property', 'category', 'category__group')

#         if self.model is SegmentDetail:
#             return SegmentDetail.objects.select_related(
#                 'property',
#                 'segment',
#                 'segment__category',
#                 'segment__category__group',
#                 'source_system',
#             )

#         return self.model.objects.select_related('property')

#     def apply_search(self, queryset, q):
#         if self.model is SegmentGroup:
#             return queryset.filter(
#                 Q(code__icontains=q) |
#                 Q(name__icontains=q)
#             )

#         if self.model is SegmentCategory:
#             return queryset.filter(
#                 Q(code__icontains=q) |
#                 Q(name__icontains=q) |
#                 Q(group__name__icontains=q) |
#                 Q(group__code__icontains=q)
#             )

#         if self.model is Segment:
#             return queryset.filter(
#                 Q(code__icontains=q) |
#                 Q(name__icontains=q) |
#                 Q(category__name__icontains=q) |
#                 Q(category__code__icontains=q) |
#                 Q(category__group__name__icontains=q) |
#                 Q(category__group__code__icontains=q)
#             )

#         if self.model is SegmentDetail:
#             return queryset.filter(
#                 Q(code__icontains=q) |
#                 Q(name__icontains=q) |
#                 Q(description__icontains=q) |
#                 Q(segment__name__icontains=q) |
#                 Q(segment__code__icontains=q) |
#                 Q(segment__category__name__icontains=q) |
#                 Q(segment__category__group__name__icontains=q)
#             )

#         return queryset

#     def get_queryset(self):
#         queryset = filter_queryset_for_user(
#             self.get_base_queryset(),
#             self.request.user,
#         )

#         self.filter_form = self.filter_form_class(self.request.GET or None, actor=self.request.user)

#         if self.filter_form.is_valid():
#             cleaned = self.filter_form.cleaned_data
#             q = cleaned.get('q')
#             if q:
#                 queryset = self.apply_search(queryset, q)

#             if cleaned.get('property'):
#                 queryset = queryset.filter(property=cleaned['property'])

#             if cleaned.get('is_active') == 'active':
#                 queryset = queryset.filter(is_active=True)
#             elif cleaned.get('is_active') == 'inactive':
#                 queryset = queryset.filter(is_active=False)

#             if self.model is SegmentDetail:
#                 if cleaned.get('review_required') == 'yes':
#                     queryset = queryset.filter(is_review_required=True)
#                 elif cleaned.get('review_required') == 'no':
#                     queryset = queryset.filter(is_review_required=False)

#         return queryset.distinct().order_by('property__name', 'sort_order', 'name')


#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['page_title'] = self.page_title
#         context['filter_form'] = getattr(self, 'filter_form', self.filter_form_class(actor=self.request.user))
#         context['can_manage'] = can_manage_mappings(self.request.user)
#         context['breadcrumbs'] = [
#             ('Dashboard', reverse('dashboard:home')),
#             ('Settings', ''),
#             ('Mappings', reverse('settings_mappings:overview')),
#             ('Market Segmentation', reverse('settings_mappings:segment-detail-list')),
#             (self.page_title, ''),
#         ]

#         querydict = self.request.GET.copy()
#         querydict.pop('page', None)
#         context['current_query'] = querydict.urlencode()

#         page_obj = context.get('page_obj')
#         paginator = context.get('paginator')
#         if page_obj and paginator:
#             current = page_obj.number
#             total = paginator.num_pages
#             start = max(current - 2, 1)
#             end = min(current + 2, total)
#             context['page_range_window'] = range(start, end + 1)

#         category_options_by_property = defaultdict(list)
#         for obj in filter_queryset_for_user(
#             SegmentCategory.objects.filter(is_active=True).select_related('property', 'group'),
#             self.request.user,
#         ).order_by('property__name', 'group__sort_order', 'sort_order', 'name'):
#             category_options_by_property[obj.property_id].append(obj)

#         group_options_by_property = defaultdict(list)
#         for obj in filter_queryset_for_user(
#             SegmentGroup.objects.filter(is_active=True).select_related('property'),
#             self.request.user,
#         ).order_by('property__name', 'sort_order', 'name'):
#             group_options_by_property[obj.property_id].append(obj)

#         segment_options_by_property = defaultdict(list)
#         for obj in filter_queryset_for_user(
#             Segment.objects.filter(is_active=True).select_related('property', 'category', 'category__group'),
#             self.request.user,
#         ).order_by('property__name', 'sort_order', 'name'):
#             segment_options_by_property[obj.property_id].append(obj)

#         context['category_options_by_property'] = dict(category_options_by_property)
#         context['group_options_by_property'] = dict(group_options_by_property)
#         context['segment_options_by_property'] = dict(segment_options_by_property)

#         return context


#     def get(self, request, *args, **kwargs):
#         self.object_list = self.get_queryset()

#         if self.should_export():
#             return self.render_to_csv_response(self.object_list)

#         context = self.get_context_data()
#         return self.render_to_response(context)

#     def get_export_filename(self):
#         if self.model is SegmentGroup:
#             return 'segment_groups.csv'
#         if self.model is SegmentCategory:
#             return 'segment_categories.csv'
#         if self.model is Segment:
#             return 'segments.csv'
#         return 'segment_details.csv'

#     def get_export_headers(self):
#         if self.model is SegmentGroup:
#             return [
#                 ('Property', lambda o: o.property.name),
#                 ('Code', 'code'),
#                 ('Name', 'name'),
#                 ('Description', 'description'),
#                 ('Sort Order', 'sort_order'),
#                 ('Active', lambda o: 'Yes' if o.is_active else 'No'),
#             ]

#         if self.model is SegmentCategory:
#             return [
#                 ('Property', lambda o: o.property.name),
#                 ('Code', 'code'),
#                 ('Name', 'name'),
#                 ('Group Code', lambda o: getattr(o.group, 'code', '')),
#                 ('Group Name', lambda o: getattr(o.group, 'name', '')),
#                 ('Description', 'description'),
#                 ('Sort Order', 'sort_order'),
#                 ('Active', lambda o: 'Yes' if o.is_active else 'No'),
#             ]

#         if self.model is Segment:
#             return [
#                 ('Property', lambda o: o.property.name),
#                 ('Code', 'code'),
#                 ('Name', 'name'),
#                 ('Category Code', lambda o: getattr(o.category, 'code', '')),
#                 ('Category Name', lambda o: getattr(o.category, 'name', '')),
#                 ('Group Code', lambda o: getattr(getattr(o.category, 'group', None), 'code', '')),
#                 ('Group Name', lambda o: getattr(getattr(o.category, 'group', None), 'name', '')),
#                 ('Description', 'description'),
#                 ('Sort Order', 'sort_order'),
#                 ('Active', lambda o: 'Yes' if o.is_active else 'No'),
#             ]

#         return [
#             ('Property', lambda o: o.property.name),
#             ('Code', 'code'),
#             ('Name', 'name'),
#             ('Description', 'description'),
#             ('Segment Code', lambda o: getattr(o.segment, 'code', '')),
#             ('Segment Name', lambda o: getattr(o.segment, 'name', '')),
#             ('Category Code', lambda o: getattr(getattr(o.segment, 'category', None), 'code', '')),
#             ('Category Name', lambda o: getattr(getattr(o.segment, 'category', None), 'name', '')),
#             ('Group Code', lambda o: getattr(getattr(getattr(o.segment, 'category', None), 'group', None), 'code', '')),
#             ('Group Name', lambda o: getattr(getattr(getattr(o.segment, 'category', None), 'group', None), 'name', '')),
#             ('Source System', lambda o: getattr(o.source_system, 'name', '')),
#             ('Notes', 'notes'),
#             ('Review Required', lambda o: 'Yes' if o.is_review_required else 'No'),
#             ('Effective From', lambda o: o.effective_from or ''),
#             ('Effective To', lambda o: o.effective_to or ''),
#             ('Sort Order', 'sort_order'),
#             ('Active', lambda o: 'Yes' if o.is_active else 'No'),
#         ]


#     # def get_context_data(self, **kwargs):
#     #     context = super().get_context_data(**kwargs)
#     #     context['page_title'] = self.page_title
#     #     context['filter_form'] = getattr(self, 'filter_form', self.filter_form_class(actor=self.request.user))
#     #     context['can_manage'] = can_manage_mappings(self.request.user)
#     #     context['breadcrumbs'] = [
#     #         ('Dashboard', reverse('dashboard:home')),
#     #         ('Settings', ''),
#     #         ('Mappings', reverse('settings_mappings:overview')),
#     #         ('Market Segmentation', reverse('settings_mappings:segment-detail-list')),
#     #         (self.page_title, ''),
#     #     ]

#     #     querydict = self.request.GET.copy()
#     #     querydict.pop('page', None)
#     #     context['current_query'] = querydict.urlencode()

#     #     page_obj = context.get('page_obj')
#     #     paginator = context.get('paginator')
#     #     if page_obj and paginator:
#     #         current = page_obj.number
#     #         total = paginator.num_pages
#     #         start = max(current - 2, 1)
#     #         end = min(current + 2, total)
#     #         context['page_range_window'] = range(start, end + 1)

#     #     category_options_by_property = defaultdict(list)
#     #     for obj in filter_queryset_for_user(
#     #         SegmentCategory.objects.filter(is_active=True).select_related('group'),
#     #         self.request.user,
#     #     ).order_by('group__sort_order', 'sort_order', 'name'):
#     #         category_options_by_property[obj.property_id].append(obj)

#     #     group_options_by_property = defaultdict(list)
#     #     for obj in filter_queryset_for_user(
#     #         SegmentGroup.objects.filter(is_active=True),
#     #         self.request.user,
#     #     ).order_by('sort_order', 'name'):
#     #         group_options_by_property[obj.property_id].append(obj)

#     #     segment_options_by_property = defaultdict(list)
#     #     for obj in filter_queryset_for_user(
#     #         Segment.objects.filter(is_active=True).select_related('category', 'category__group'),
#     #         self.request.user,
#     #     ).order_by('sort_order', 'name'):
#     #         segment_options_by_property[obj.property_id].append(obj)

#     #     context['category_options_by_property'] = dict(category_options_by_property)
#     #     context['group_options_by_property'] = dict(group_options_by_property)
#     #     context['segment_options_by_property'] = dict(segment_options_by_property)
        
        
#     #     return context


# class SegmentGroupListView(BaseSegmentationListView):
#     model = SegmentGroup
#     page_title = 'Segment groups'
#     filter_form_class = GroupFilterForm


# class SegmentCategoryListView(BaseSegmentationListView):
#     model = SegmentCategory
#     page_title = 'Segment categories'
#     filter_form_class = GroupFilterForm


# class SegmentListView(BaseSegmentationListView):
#     model = Segment
#     page_title = 'Segments'
#     filter_form_class = GroupFilterForm


# class SegmentDetailListView(BaseSegmentationListView):
#     model = SegmentDetail
#     page_title = 'Segment details'
#     filter_form_class = MappingFilterForm


# class SegmentGroupCreateView(BaseSegmentationCreateView):
#     form_class = SegmentGroupForm
#     page_title = 'Create segment group'
#     success_url = reverse_lazy('settings_mappings:segment-group-list')


# class SegmentCategoryCreateView(BaseSegmentationCreateView):
#     form_class = SegmentCategoryForm
#     page_title = 'Create segment category'
#     success_url = reverse_lazy('settings_mappings:segment-category-list')


# class SegmentCreateView(BaseSegmentationCreateView):
#     form_class = SegmentForm
#     page_title = 'Create segment'
#     success_url = reverse_lazy('settings_mappings:segment-list')


# class SegmentDetailCreateView(BaseSegmentationCreateView):
#     form_class = SegmentDetailForm
#     page_title = 'Create segment detail'
#     success_url = reverse_lazy('settings_mappings:segment-detail-list')


# class SegmentGroupUpdateView(BaseSegmentationUpdateView):
#     model = SegmentGroup
#     form_class = SegmentGroupForm
#     page_title = 'Edit segment group'
#     success_url = reverse_lazy('settings_mappings:segment-group-list')


# class SegmentCategoryUpdateView(BaseSegmentationUpdateView):
#     model = SegmentCategory
#     form_class = SegmentCategoryForm
#     page_title = 'Edit segment category'
#     success_url = reverse_lazy('settings_mappings:segment-category-list')


# class SegmentUpdateView(BaseSegmentationUpdateView):
#     model = Segment
#     form_class = SegmentForm
#     page_title = 'Edit segment'
#     success_url = reverse_lazy('settings_mappings:segment-list')


# class SegmentDetailUpdateView(BaseSegmentationUpdateView):
#     model = SegmentDetail
#     form_class = SegmentDetailForm
#     page_title = 'Edit segment detail'

#     def get_success_url(self):
#         return reverse('settings_mappings:segment-detail-detail', kwargs={'pk': self.object.pk})


# class SegmentDetailDetailView(SegmentationAccessMixin, BreadcrumbMixin, DetailView):
#     template_name = 'settings/mappings/segmentations/detail.html'
#     context_object_name = 'object'
#     model = SegmentDetail

#     def get_queryset(self):
#         return filter_queryset_for_user(
#             SegmentDetail.objects.select_related(
#                 'property',
#                 'segment',
#                 'segment__category',
#                 'segment__category__group',
#                 'source_system',
#             ),
#             self.request.user,
#         )

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['can_manage'] = can_manage_mappings(self.request.user)
#         context['breadcrumbs'] = [
#             ('Dashboard', reverse('dashboard:home')),
#             ('Settings', ''),
#             ('Mappings', reverse('settings_mappings:overview')),
#             ('Market Segmentation', reverse('settings_mappings:segment-detail-list')),
#             (self.object.code, ''),
#         ]
#         return context


# class SegmentOptionsView(SegmentationManageMixin, View):
#     def get(self, request, *args, **kwargs):
#         property_id = request.GET.get('property_id')

#         queryset = filter_queryset_for_user(
#             Segment.objects.filter(is_active=True).select_related('category', 'category__group'),
#             request.user,
#         )

#         if property_id:
#             queryset = queryset.filter(property_id=property_id)
#         else:
#             queryset = queryset.none()

#         return JsonResponse({
#             'results': [
#                 {
#                     'id': obj.id,
#                     'name': obj.name,
#                     'code': obj.code,
#                 }
#                 for obj in queryset.order_by('name')
#             ]
#         })


# class SegmentGroupOptionsView(SegmentationManageMixin, View):
#     def get(self, request, *args, **kwargs):
#         property_id = request.GET.get('property_id')

#         queryset = filter_queryset_for_user(
#             SegmentGroup.objects.filter(is_active=True),
#             request.user,
#         )

#         if property_id:
#             queryset = queryset.filter(property_id=property_id)
#         else:
#             queryset = queryset.none()

#         return JsonResponse({
#             'results': [
#                 {
#                     'id': obj.id,
#                     'name': obj.name,
#                     'code': obj.code,
#                 }
#                 for obj in queryset.order_by('name')
#             ]
#         })


# class SegmentCategoryOptionsView(SegmentationManageMixin, View):
#     def get(self, request, *args, **kwargs):
#         property_id = request.GET.get('property_id')

#         queryset = filter_queryset_for_user(
#             SegmentCategory.objects.filter(is_active=True).select_related('group'),
#             request.user,
#         )

#         if property_id:
#             queryset = queryset.filter(property_id=property_id)
#         else:
#             queryset = queryset.none()

#         return JsonResponse({
#             'results': [
#                 {
#                     'id': obj.id,
#                     'name': obj.name,
#                     'code': obj.code,
#                 }
#                 for obj in queryset.order_by('group__sort_order', 'sort_order', 'name')
#             ]
#         })





# from django.http import HttpResponseBadRequest
# from django.shortcuts import get_object_or_404, render
# from django.views import View

# from apps.core.common.access import filter_queryset_for_user
# from apps.settings.mappings.models import Segment, SegmentCategory, SegmentDetail, SegmentGroup


# class BaseSegmentationInlineUpdateView(SegmentationManageMixin, View):
#     model = None
#     field_name = None
#     related_model = None
#     partial_template_name = 'settings/mappings/segmentations/partials/inline_relation_cell.html'
#     option_context_name = 'options'
#     display_attr = 'name'

#     def get_object_queryset(self):
#         return filter_queryset_for_user(
#             self.model.objects.select_related('property'),
#             self.request.user,
#         )

#     def get_related_queryset(self, obj):
#         return filter_queryset_for_user(
#             self.related_model.objects.filter(
#                 property_id=obj.property_id,
#                 is_active=True,
#             ),
#             self.request.user,
#         ).order_by('sort_order', 'name')

#     def get(self, request, *args, **kwargs):
#         obj = get_object_or_404(self.get_object_queryset(), pk=kwargs['pk'])
#         return self.render_cell(obj)

#     def post(self, request, *args, **kwargs):
#         obj = get_object_or_404(self.get_object_queryset(), pk=kwargs['pk'])

#         value = request.POST.get(self.field_name)
#         if not value:
#             return HttpResponseBadRequest(f'Missing {self.field_name}.')

#         related_obj = get_object_or_404(self.get_related_queryset(obj), pk=value)
#         setattr(obj, self.field_name, related_obj)
#         obj.save(update_fields=[self.field_name])
#         obj.refresh_from_db()

#         return self.render_cell(obj)

#     def render_cell(self, obj):
#         current_related = getattr(obj, self.field_name, None)
#         return render(
#             self.request,
#             self.partial_template_name,
#             {
#                 'object': obj,
#                 'field_name': self.field_name,
#                 'display_value': getattr(current_related, self.display_attr, '—'),
#                 'current_related_id': getattr(current_related, 'pk', None),
#                 self.option_context_name: self.get_related_queryset(obj),
#                 'post_url': self.request.path,
#             },
#         )


# class SegmentInlineCategoryUpdateView(BaseSegmentationInlineUpdateView):
#     model = Segment
#     field_name = 'category'
#     related_model = SegmentCategory

#     def get_object_queryset(self):
#         return filter_queryset_for_user(
#             Segment.objects.select_related('property', 'category', 'category__group'),
#             self.request.user,
#         )


# class SegmentDetailInlineSegmentUpdateView(BaseSegmentationInlineUpdateView):
#     model = SegmentDetail
#     field_name = 'segment'
#     related_model = Segment

#     def get_object_queryset(self):
#         return filter_queryset_for_user(
#             SegmentDetail.objects.select_related(
#                 'property',
#                 'segment',
#                 'segment__category',
#                 'segment__category__group',
#             ),
#             self.request.user,
#         )


# class SegmentCategoryInlineGroupUpdateView(BaseSegmentationInlineUpdateView):
#     model = SegmentCategory
#     field_name = 'group'
#     related_model = SegmentGroup

#     def get_object_queryset(self):
#         return filter_queryset_for_user(
#             SegmentCategory.objects.select_related('property', 'group'),
#             self.request.user,
#         )


