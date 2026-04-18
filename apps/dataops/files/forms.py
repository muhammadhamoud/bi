from django import forms

from apps.core.common.forms import StyledFormMixin
from apps.dataops.files.models import FileRecord, SourceSystem
from apps.properties.core.selectors import get_accessible_properties


class FileFilterForm(StyledFormMixin, forms.Form):
    q = forms.CharField(required=False, label='Search')
    property = forms.ModelChoiceField(required=False, queryset=None)
    source_system = forms.ModelChoiceField(required=False, queryset=SourceSystem.objects.none())
    file_type = forms.CharField(required=False)
    status = forms.ChoiceField(required=False, choices=[('', 'All statuses')] + list(FileRecord.LifecycleStatus.choices))
    start_date = forms.DateField(required=False, widget=forms.DateInput())
    end_date = forms.DateField(required=False, widget=forms.DateInput())

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['property'].queryset = get_accessible_properties(user)
        self.fields['source_system'].queryset = SourceSystem.objects.filter(is_active=True).order_by('name')
