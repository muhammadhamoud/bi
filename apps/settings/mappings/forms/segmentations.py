# from django import forms
# from bi.apps.settings.mappings.forms.common_ import BaseMappingModelForm
# from apps.settings.mappings.models import Segment, SegmentCategory, SegmentDetail, SegmentGroup


# class SegmentGroupForm(BaseMappingModelForm):
#     class Meta:
#         model = SegmentGroup
#         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


# class SegmentCategoryForm(BaseMappingModelForm):
#     class Meta:
#         model = SegmentCategory
#         fields = ['property', 'group', 'code', 'name', 'description', 'sort_order', 'is_active']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.fields['group'].queryset = SegmentGroup.objects.none()

#         if self.is_bound:
#             property_id = self.data.get('property')
#             if property_id:
#                 self.fields['group'].queryset = SegmentGroup.objects.filter(
#                     property_id=property_id
#                 ).order_by('name')
#         elif self.instance and self.instance.pk and self.instance.property_id:
#             self.fields['group'].queryset = SegmentGroup.objects.filter(
#                 property=self.instance.property
#             ).order_by('name')
#         elif self.initial.get('property'):
#             self.fields['group'].queryset = SegmentGroup.objects.filter(
#                 property=self.initial['property']
#             ).order_by('name')

#     def clean_group(self):
#         group = self.cleaned_data.get('group')
#         property_obj = self.cleaned_data.get('property')

#         if group and property_obj and group.property_id != property_obj.id:
#             raise forms.ValidationError('Selected group must belong to the selected property.')

#         return group


# class SegmentForm(BaseMappingModelForm):
#     class Meta:
#         model = Segment
#         fields = ['property', 'category', 'code', 'name', 'description', 'sort_order', 'is_active']

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.fields['category'].queryset = SegmentCategory.objects.none()

#         if self.is_bound:
#             property_id = self.data.get('property')
#             if property_id:
#                 self.fields['category'].queryset = SegmentCategory.objects.filter(
#                     property_id=property_id
#                 ).select_related('group').order_by('group__name', 'name')
#         elif self.instance and self.instance.pk and self.instance.property_id:
#             self.fields['category'].queryset = SegmentCategory.objects.filter(
#                 property=self.instance.property
#             ).select_related('group').order_by('group__name', 'name')
#         elif self.initial.get('property'):
#             self.fields['category'].queryset = SegmentCategory.objects.filter(
#                 property=self.initial['property']
#             ).select_related('group').order_by('group__name', 'name')

#     def clean_category(self):
#         category = self.cleaned_data.get('category')
#         property_obj = self.cleaned_data.get('property')

#         if category and property_obj and category.property_id != property_obj.id:
#             raise forms.ValidationError('Selected category must belong to the selected property.')

#         return category


# class SegmentDetailForm(BaseMappingModelForm):
#     class Meta:
#         model = SegmentDetail
#         fields = [
#             'property', 'mapping', 'code', 'name', 'description',
#             'notes', 'effective_from', 'effective_to', 'sort_order',
#             'source_system', 'is_active', 'is_review_required'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.fields['mapping'].queryset = Segment.objects.none()

#         if self.is_bound:
#             property_id = self.data.get('property')
#             if property_id:
#                 self.fields['mapping'].queryset = Segment.objects.filter(
#                     property_id=property_id
#                 ).select_related('category', 'category__group').order_by('name')
#         elif self.instance and self.instance.pk and self.instance.property_id:
#             self.fields['mapping'].queryset = Segment.objects.filter(
#                 property=self.instance.property
#             ).select_related('category', 'category__group').order_by('name')
#         elif self.initial.get('property'):
#             self.fields['mapping'].queryset = Segment.objects.filter(
#                 property=self.initial['property']
#             ).select_related('category', 'category__group').order_by('name')

#     def clean_mapping(self):
#         mapping = self.cleaned_data.get('mapping')
#         property_obj = self.cleaned_data.get('property')

#         if mapping and property_obj and mapping.property_id != property_obj.id:
#             raise forms.ValidationError('Selected mapping must belong to the selected property.')

#         return mapping

