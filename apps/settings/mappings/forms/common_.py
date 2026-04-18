# from django import forms

# from apps.core.common.forms import StyledFormMixin
# from apps.properties.core.selectors import get_accessible_properties
# from apps.settings.mappings.models import (
#     CompanyGroup,
#     CompanyMapping,
#     CompetitorGroup,
#     CompetitorMapping,
#     DayOfWeekGroup,
#     DayOfWeekMapping,
#     GuestCountryGroup,
#     GuestCountryMapping,
#     LoyaltyGroup,
#     LoyaltyMapping,
#     OriginGroup,
#     OriginMapping,
#     PackageGroup,
#     PackageMapping,
#     RateCodeGroup,
#     RateCodeMapping,
#     RoomTypeGroup,
#     RoomTypeMapping,
#     TravelAgentGroup,
#     TravelAgentMapping,
# )


# class BaseMappingModelForm(StyledFormMixin, forms.ModelForm):
#     def __init__(self, *args, actor=None, **kwargs):
#         self.actor = actor
#         super().__init__(*args, **kwargs)

#         properties = get_accessible_properties(actor)
#         property_ids = list(properties.values_list('id', flat=True))

#         if 'property' in self.fields:
#             self.fields['property'].queryset = properties

#         selected_property_id = self.data.get('property') or getattr(self.instance, 'property_id', None)

#         for _, field in self.fields.items():
#             if isinstance(field, (forms.ModelChoiceField, forms.ModelMultipleChoiceField)) and field.queryset is not None:
#                 try:
#                     model_field_names = {f.name for f in field.queryset.model._meta.fields}
#                 except Exception:
#                     model_field_names = set()

#                 if 'property' in model_field_names:
#                     queryset = field.queryset.filter(property_id__in=property_ids)
#                     if selected_property_id and field.queryset.model.__name__ != 'Property':
#                         queryset = queryset.filter(property_id=selected_property_id)
#                     field.queryset = queryset.distinct()


# class PropertyScopedRelationFormMixin:
#     relation_field_name = None
#     relation_model = None
#     relation_select_related = ()
#     relation_ordering = ()
#     relation_error_message = 'Selected value must belong to the selected property.'

#     def setup_property_scoped_relation_field(self):
#         field_name = self.relation_field_name
#         model = self.relation_model

#         if not field_name or not model or field_name not in self.fields:
#             return

#         self.fields[field_name].queryset = model.objects.none()

#         if self.is_bound:
#             property_id = self.data.get('property')
#             if property_id:
#                 queryset = model.objects.filter(property_id=property_id)
#             else:
#                 queryset = model.objects.none()
#         elif self.instance and self.instance.pk and getattr(self.instance, 'property_id', None):
#             queryset = model.objects.filter(property=self.instance.property)
#         elif self.initial.get('property'):
#             queryset = model.objects.filter(property=self.initial['property'])
#         else:
#             queryset = model.objects.none()

#         if self.relation_select_related:
#             queryset = queryset.select_related(*self.relation_select_related)

#         if self.relation_ordering:
#             queryset = queryset.order_by(*self.relation_ordering)

#         self.fields[field_name].queryset = queryset

#     def validate_property_scoped_relation(self, field_name=None, error_message=None):
#         field_name = field_name or self.relation_field_name
#         value = self.cleaned_data.get(field_name)
#         property_obj = self.cleaned_data.get('property')

#         if value and property_obj and getattr(value, 'property_id', None) != property_obj.id:
#             raise forms.ValidationError(error_message or self.relation_error_message)

#         return value


# class MappingFilterForm(StyledFormMixin, forms.Form):
#     q = forms.CharField(required=False, label='Search')
#     property = forms.ModelChoiceField(required=False, queryset=None)
#     is_active = forms.ChoiceField(required=False, choices=[('', 'All'), ('active', 'Active'), ('inactive', 'Inactive')])
#     review_required = forms.ChoiceField(required=False, choices=[('', 'All'), ('yes', 'Needs review'), ('no', 'Ready')])

#     def __init__(self, *args, actor=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['property'].queryset = get_accessible_properties(actor)


# class GroupFilterForm(StyledFormMixin, forms.Form):
#     q = forms.CharField(required=False, label='Search')
#     property = forms.ModelChoiceField(required=False, queryset=None)
#     is_active = forms.ChoiceField(required=False, choices=[('', 'All'), ('active', 'Active'), ('inactive', 'Inactive')])

#     def __init__(self, *args, actor=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['property'].queryset = get_accessible_properties(actor)


# class RoomTypeGroupForm(BaseMappingModelForm):
#     class Meta:
#         model = RoomTypeGroup
#         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


# class RoomTypeMappingForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
#     relation_field_name = 'group'
#     relation_model = RoomTypeGroup
#     relation_ordering = ('name',)
#     relation_error_message = 'Selected group must belong to the selected property.'

#     class Meta:
#         model = RoomTypeMapping
#         fields = [
#             'property', 'group', 'source_system', 'code', 'name', 'description',
#             'notes', 'is_review_required', 'effective_from', 'effective_to',
#             'sort_order', 'is_active'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.setup_property_scoped_relation_field()

#     def clean_group(self):
#         return self.validate_property_scoped_relation('group', self.relation_error_message)


# class PackageGroupForm(BaseMappingModelForm):
#     class Meta:
#         model = PackageGroup
#         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


# class PackageMappingForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
#     relation_field_name = 'group'
#     relation_model = PackageGroup
#     relation_ordering = ('name',)
#     relation_error_message = 'Selected group must belong to the selected property.'

#     class Meta:
#         model = PackageMapping
#         fields = [
#             'property', 'group', 'source_system', 'code', 'name', 'description',
#             'notes', 'is_review_required', 'effective_from', 'effective_to',
#             'sort_order', 'is_active'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.setup_property_scoped_relation_field()

#     def clean_group(self):
#         return self.validate_property_scoped_relation('group', self.relation_error_message)


# class RateCodeGroupForm(BaseMappingModelForm):
#     class Meta:
#         model = RateCodeGroup
#         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


# class RateCodeMappingForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
#     relation_field_name = 'group'
#     relation_model = RateCodeGroup
#     relation_ordering = ('name',)
#     relation_error_message = 'Selected group must belong to the selected property.'

#     class Meta:
#         model = RateCodeMapping
#         fields = [
#             'property', 'group', 'source_system', 'code', 'name', 'description',
#             'notes', 'is_review_required', 'effective_from', 'effective_to',
#             'sort_order', 'is_active'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.setup_property_scoped_relation_field()

#     def clean_group(self):
#         return self.validate_property_scoped_relation('group', self.relation_error_message)


# class TravelAgentGroupForm(BaseMappingModelForm):
#     class Meta:
#         model = TravelAgentGroup
#         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


# class TravelAgentMappingForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
#     relation_field_name = 'group'
#     relation_model = TravelAgentGroup
#     relation_ordering = ('name',)
#     relation_error_message = 'Selected group must belong to the selected property.'

#     class Meta:
#         model = TravelAgentMapping
#         fields = [
#             'property', 'group', 'source_system', 'code', 'name', 'description',
#             'notes', 'is_review_required', 'effective_from', 'effective_to',
#             'sort_order', 'is_active'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.setup_property_scoped_relation_field()

#     def clean_group(self):
#         return self.validate_property_scoped_relation('group', self.relation_error_message)


# class GuestCountryGroupForm(BaseMappingModelForm):
#     class Meta:
#         model = GuestCountryGroup
#         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


# class GuestCountryMappingForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
#     relation_field_name = 'group'
#     relation_model = GuestCountryGroup
#     relation_ordering = ('name',)
#     relation_error_message = 'Selected group must belong to the selected property.'

#     class Meta:
#         model = GuestCountryMapping
#         fields = [
#             'property', 'group', 'source_system', 'code', 'name', 'description',
#             'notes', 'is_review_required', 'effective_from', 'effective_to',
#             'sort_order', 'is_active'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.setup_property_scoped_relation_field()

#     def clean_group(self):
#         return self.validate_property_scoped_relation('group', self.relation_error_message)


# class CompanyGroupForm(BaseMappingModelForm):
#     class Meta:
#         model = CompanyGroup
#         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


# class CompanyMappingForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
#     relation_field_name = 'group'
#     relation_model = CompanyGroup
#     relation_ordering = ('name',)
#     relation_error_message = 'Selected group must belong to the selected property.'

#     class Meta:
#         model = CompanyMapping
#         fields = [
#             'property', 'group', 'source_system', 'code', 'name', 'description',
#             'notes', 'is_review_required', 'effective_from', 'effective_to',
#             'sort_order', 'is_active'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.setup_property_scoped_relation_field()

#     def clean_group(self):
#         return self.validate_property_scoped_relation('group', self.relation_error_message)


# class DayOfWeekGroupForm(BaseMappingModelForm):
#     class Meta:
#         model = DayOfWeekGroup
#         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


# class DayOfWeekMappingForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
#     relation_field_name = 'group'
#     relation_model = DayOfWeekGroup
#     relation_ordering = ('name',)
#     relation_error_message = 'Selected group must belong to the selected property.'

#     class Meta:
#         model = DayOfWeekMapping
#         fields = [
#             'property', 'group', 'source_system', 'code', 'name', 'description',
#             'notes', 'is_review_required', 'effective_from', 'effective_to',
#             'sort_order', 'is_active'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.setup_property_scoped_relation_field()

#     def clean_group(self):
#         return self.validate_property_scoped_relation('group', self.relation_error_message)


# class OriginGroupForm(BaseMappingModelForm):
#     class Meta:
#         model = OriginGroup
#         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


# class OriginMappingForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
#     relation_field_name = 'group'
#     relation_model = OriginGroup
#     relation_ordering = ('name',)
#     relation_error_message = 'Selected group must belong to the selected property.'

#     class Meta:
#         model = OriginMapping
#         fields = [
#             'property', 'group', 'source_system', 'code', 'name', 'description',
#             'notes', 'is_review_required', 'effective_from', 'effective_to',
#             'sort_order', 'is_active'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.setup_property_scoped_relation_field()

#     def clean_group(self):
#         return self.validate_property_scoped_relation('group', self.relation_error_message)


# class CompetitorGroupForm(BaseMappingModelForm):
#     class Meta:
#         model = CompetitorGroup
#         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


# class CompetitorMappingForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
#     relation_field_name = 'group'
#     relation_model = CompetitorGroup
#     relation_ordering = ('name',)
#     relation_error_message = 'Selected group must belong to the selected property.'

#     class Meta:
#         model = CompetitorMapping
#         fields = [
#             'property', 'group', 'source_system', 'code', 'name', 'description',
#             'notes', 'is_review_required', 'effective_from', 'effective_to',
#             'sort_order', 'is_active'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.setup_property_scoped_relation_field()

#     def clean_group(self):
#         return self.validate_property_scoped_relation('group', self.relation_error_message)


# class LoyaltyGroupForm(BaseMappingModelForm):
#     class Meta:
#         model = LoyaltyGroup
#         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']


# class LoyaltyMappingForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
#     relation_field_name = 'group'
#     relation_model = LoyaltyGroup
#     relation_ordering = ('name',)
#     relation_error_message = 'Selected group must belong to the selected property.'

#     class Meta:
#         model = LoyaltyMapping
#         fields = [
#             'property', 'group', 'source_system', 'code', 'name', 'description',
#             'notes', 'is_review_required', 'effective_from', 'effective_to',
#             'sort_order', 'is_active'
#         ]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.setup_property_scoped_relation_field()

#     def clean_group(self):
#         return self.validate_property_scoped_relation('group', self.relation_error_message)
    
    


# # from django import forms

# # from apps.core.common.forms import StyledFormMixin
# # from apps.properties.core.selectors import get_accessible_properties
# # from apps.settings.mappings.models import (
# #     RoomTypeGroup,
# #     RoomTypeMapping,
# #     PackageGroup,
# #     PackageMapping,
# #     RateCodeGroup,
# #     RateCodeMapping,
# #     TravelAgentGroup,
# #     TravelAgentMapping,
# #     GuestCountryGroup,
# #     GuestCountryMapping,
# #     CompanyGroup,
# #     CompanyMapping,
# #     DayOfWeekGroup,
# #     DayOfWeekMapping,
# #     BookingSourceGroup,
# #     BookingSourceCategory,
# #     BookingSourceMapping,
# #     OriginGroup,
# #     OriginMapping,
# #     CompetitorGroup,
# #     CompetitorMapping,
# #     LoyaltyGroup,
# #     LoyaltyMapping,
# # )


# # class BaseMappingModelForm(StyledFormMixin, forms.ModelForm):
# #     def __init__(self, *args, actor=None, **kwargs):
# #         self.actor = actor
# #         super().__init__(*args, **kwargs)
# #         properties = get_accessible_properties(actor)
# #         property_ids = list(properties.values_list('id', flat=True))
# #         if 'property' in self.fields:
# #             self.fields['property'].queryset = properties
# #         selected_property_id = self.data.get('property') or getattr(self.instance, 'property_id', None)
# #         for field in self.fields.values():
# #             if isinstance(field, (forms.ModelChoiceField, forms.ModelMultipleChoiceField)) and field.queryset is not None:
# #                 try:
# #                     model_field_names = {f.name for f in field.queryset.model._meta.fields}
# #                 except Exception:
# #                     model_field_names = set()
# #                 if 'property' in model_field_names:
# #                     queryset = field.queryset.filter(property_id__in=property_ids)
# #                     if selected_property_id and field.queryset.model.__name__ != "Property":
# #                         queryset = queryset.filter(property_id=selected_property_id)
# #                     field.queryset = queryset.distinct()


# # class MappingFilterForm(StyledFormMixin, forms.Form):
# #     q = forms.CharField(required=False, label='Search')
# #     property = forms.ModelChoiceField(required=False, queryset=None)
# #     is_active = forms.ChoiceField(required=False, choices=[('', 'All'), ('active', 'Active'), ('inactive', 'Inactive')])
# #     review_required = forms.ChoiceField(required=False, choices=[('', 'All'), ('yes', 'Needs review'), ('no', 'Ready')])

# #     def __init__(self, *args, actor=None, **kwargs):
# #         super().__init__(*args, **kwargs)
# #         self.fields['property'].queryset = get_accessible_properties(actor)


# # class GroupFilterForm(StyledFormMixin, forms.Form):
# #     q = forms.CharField(required=False, label='Search')
# #     property = forms.ModelChoiceField(required=False, queryset=None)
# #     is_active = forms.ChoiceField(required=False, choices=[('', 'All'), ('active', 'Active'), ('inactive', 'Inactive')])

# #     def __init__(self, *args, actor=None, **kwargs):
# #         super().__init__(*args, **kwargs)
# #         self.fields['property'].queryset = get_accessible_properties(actor)


# # class RoomTypeGroupForm(BaseMappingModelForm):
# #     class Meta:
# #         model = RoomTypeGroup
# #         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']

# # class RoomTypeMappingForm(BaseMappingModelForm):
# #     class Meta:
# #         model = RoomTypeMapping
# #         fields = ['property', 'group', 'source_system', 'code', 'name', 'description', 'notes', 'is_review_required', 'effective_from', 'effective_to', 'sort_order', 'is_active']

# # class PackageGroupForm(BaseMappingModelForm):
# #     class Meta:
# #         model = PackageGroup
# #         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']

# # class PackageMappingForm(BaseMappingModelForm):
# #     class Meta:
# #         model = PackageMapping
# #         fields = ['property', 'group', 'source_system', 'code', 'name', 'description', 'notes', 'is_review_required', 'effective_from', 'effective_to', 'sort_order', 'is_active']

# # class RateCodeGroupForm(BaseMappingModelForm):
# #     class Meta:
# #         model = RateCodeGroup
# #         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']

# # class RateCodeMappingForm(BaseMappingModelForm):
# #     class Meta:
# #         model = RateCodeMapping
# #         fields = ['property', 'group', 'source_system', 'code', 'name', 'description', 'notes', 'is_review_required', 'effective_from', 'effective_to', 'sort_order', 'is_active']

# # class TravelAgentGroupForm(BaseMappingModelForm):
# #     class Meta:
# #         model = TravelAgentGroup
# #         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']

# # class TravelAgentMappingForm(BaseMappingModelForm):
# #     class Meta:
# #         model = TravelAgentMapping
# #         fields = ['property', 'group', 'source_system', 'code', 'name', 'description', 'notes', 'is_review_required', 'effective_from', 'effective_to', 'sort_order', 'is_active']

# # class GuestCountryGroupForm(BaseMappingModelForm):
# #     class Meta:
# #         model = GuestCountryGroup
# #         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']

# # class GuestCountryMappingForm(BaseMappingModelForm):
# #     class Meta:
# #         model = GuestCountryMapping
# #         fields = ['property', 'group', 'source_system', 'code', 'name', 'description', 'notes', 'is_review_required', 'effective_from', 'effective_to', 'sort_order', 'is_active']

# # class CompanyGroupForm(BaseMappingModelForm):
# #     class Meta:
# #         model = CompanyGroup
# #         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']

# # class CompanyMappingForm(BaseMappingModelForm):
# #     class Meta:
# #         model = CompanyMapping
# #         fields = ['property', 'group', 'source_system', 'code', 'name', 'description', 'notes', 'is_review_required', 'effective_from', 'effective_to', 'sort_order', 'is_active']

# # class DayOfWeekGroupForm(BaseMappingModelForm):
# #     class Meta:
# #         model = DayOfWeekGroup
# #         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']

# # class DayOfWeekMappingForm(BaseMappingModelForm):
# #     class Meta:
# #         model = DayOfWeekMapping
# #         fields = ['property', 'group', 'source_system', 'code', 'name', 'description', 'notes', 'is_review_required', 'effective_from', 'effective_to', 'sort_order', 'is_active']

# # class BookingSourceGroupForm(BaseMappingModelForm):
# #     class Meta:
# #         model = BookingSourceGroup
# #         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']

# # class BookingSourceCategoryForm(BaseMappingModelForm):
# #     class Meta:
# #         model = BookingSourceCategory
# #         fields = ['property', 'group' ,'code', 'name', 'description', 'sort_order', 'is_active']

# # class BookingSourceMappingForm(BaseMappingModelForm):
# #     class Meta:
# #         model = BookingSourceMapping
# #         fields = ['property', 'category', 'source_system', 'code', 'name', 'description', 'notes', 'is_review_required', 'effective_from', 'effective_to', 'sort_order', 'is_active']

# # class OriginGroupForm(BaseMappingModelForm):
# #     class Meta:
# #         model = OriginGroup
# #         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']

# # class OriginMappingForm(BaseMappingModelForm):
# #     class Meta:
# #         model = OriginMapping
# #         fields = ['property', 'group', 'source_system', 'code', 'name', 'description', 'notes', 'is_review_required', 'effective_from', 'effective_to', 'sort_order', 'is_active']

# # class CompetitorGroupForm(BaseMappingModelForm):
# #     class Meta:
# #         model = CompetitorGroup
# #         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']

# # class CompetitorMappingForm(BaseMappingModelForm):
# #     class Meta:
# #         model = CompetitorMapping
# #         fields = ['property', 'group', 'source_system', 'code', 'name', 'description', 'notes', 'is_review_required', 'effective_from', 'effective_to', 'sort_order', 'is_active']

# # class LoyaltyGroupForm(BaseMappingModelForm):
# #     class Meta:
# #         model = LoyaltyGroup
# #         fields = ['property', 'code', 'name', 'description', 'sort_order', 'is_active']

# # class LoyaltyMappingForm(BaseMappingModelForm):
# #     class Meta:
# #         model = LoyaltyMapping
# #         fields = ['property', 'group', 'source_system', 'code', 'name', 'description', 'notes', 'is_review_required', 'effective_from', 'effective_to', 'sort_order', 'is_active']
