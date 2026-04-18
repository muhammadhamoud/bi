from django import forms

from apps.properties.core.selectors import get_accessible_properties
from apps.core.common.forms import StyledFormMixin


class BaseMappingModelForm(StyledFormMixin, forms.ModelForm):
    def __init__(self, *args, actor=None, **kwargs):
        self.actor = actor
        super().__init__(*args, **kwargs)

        properties = get_accessible_properties(actor)
        property_ids = list(properties.values_list('id', flat=True))

        if 'property' in self.fields:
            self.fields['property'].queryset = properties

        selected_property_id = (
            self.data.get('property')
            or getattr(self.instance, 'property_id', None)
            or self.initial.get('property')
        )

        for _, field in self.fields.items():
            if isinstance(field, (forms.ModelChoiceField, forms.ModelMultipleChoiceField)) and field.queryset is not None:
                try:
                    model_field_names = {f.name for f in field.queryset.model._meta.fields}
                except Exception:
                    model_field_names = set()

                if 'property' in model_field_names:
                    queryset = field.queryset.filter(property_id__in=property_ids)

                    if selected_property_id and field.queryset.model.__name__ != 'Property':
                        queryset = queryset.filter(property_id=selected_property_id)

                    field.queryset = queryset.distinct()


class PropertyScopedRelationFormMixin:
    relation_field_name = None
    relation_model = None
    relation_select_related = ()
    relation_ordering = ()
    relation_error_message = 'Selected value must belong to the selected property.'

    def setup_property_scoped_relation_field(self):
        field_name = self.relation_field_name
        model = self.relation_model

        if not field_name or not model or field_name not in self.fields:
            return

        queryset = model.objects.none()

        if self.is_bound:
            property_id = self.data.get('property')
            if property_id:
                queryset = model.objects.filter(property_id=property_id)
        elif self.instance and self.instance.pk and getattr(self.instance, 'property_id', None):
            queryset = model.objects.filter(property=self.instance.property)
        elif self.initial.get('property'):
            queryset = model.objects.filter(property=self.initial['property'])

        if self.relation_select_related:
            queryset = queryset.select_related(*self.relation_select_related)

        if self.relation_ordering:
            queryset = queryset.order_by(*self.relation_ordering)

        self.fields[field_name].queryset = queryset

    def validate_property_scoped_relation(self, field_name=None, error_message=None):
        field_name = field_name or self.relation_field_name
        value = self.cleaned_data.get(field_name)
        property_obj = self.cleaned_data.get('property')

        if value and property_obj and getattr(value, 'property_id', None) != property_obj.id:
            raise forms.ValidationError(error_message or self.relation_error_message)

        return value


class BaseGroupForm(BaseMappingModelForm):
    pass


class BaseCategoryForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
    relation_field_name = 'group'
    relation_ordering = ('name',)
    relation_error_message = 'Selected group must belong to the selected property.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_property_scoped_relation_field()

    def clean_group(self):
        return self.validate_property_scoped_relation('group', self.relation_error_message)


class BaseHierarchyMappingForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
    relation_field_name = 'category'
    relation_select_related = ('group',)
    relation_ordering = ('group__name', 'name')
    relation_error_message = 'Selected category must belong to the selected property.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_property_scoped_relation_field()

    def clean_category(self):
        return self.validate_property_scoped_relation('category', self.relation_error_message)


class BaseHierarchyDetailForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
    relation_field_name = 'mapping'
    relation_select_related = ('category', 'category__group')
    relation_ordering = ('category__group__name', 'category__name', 'name')
    relation_error_message = 'Selected mapping must belong to the selected property.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_property_scoped_relation_field()

    def clean_mapping(self):
        return self.validate_property_scoped_relation('mapping', self.relation_error_message)


class MappingFilterForm(StyledFormMixin, forms.Form):
    q = forms.CharField(required=False, label='Search')
    property = forms.ModelChoiceField(required=False, queryset=None)
    is_active = forms.ChoiceField(
        required=False,
        choices=[('', 'All'), ('active', 'Active'), ('inactive', 'Inactive')],
    )
    review_required = forms.ChoiceField(
        required=False,
        choices=[('', 'All'), ('yes', 'Needs review'), ('no', 'Ready')],
    )

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['property'].queryset = get_accessible_properties(actor)


class GroupFilterForm(StyledFormMixin, forms.Form):
    q = forms.CharField(required=False, label='Search')
    property = forms.ModelChoiceField(required=False, queryset=None)
    is_active = forms.ChoiceField(
        required=False,
        choices=[('', 'All'), ('active', 'Active'), ('inactive', 'Inactive')],
    )

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['property'].queryset = get_accessible_properties(actor)


class BaseSimpleMappingForm(PropertyScopedRelationFormMixin, BaseMappingModelForm):
    relation_field_name = 'group'
    relation_ordering = ('name',)
    relation_error_message = 'Selected group must belong to the selected property.'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_property_scoped_relation_field()

    def clean_group(self):
        return self.validate_property_scoped_relation('group', self.relation_error_message)
