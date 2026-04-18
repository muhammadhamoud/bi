from django import forms
from django.utils import timezone

from apps.core.common.forms import StyledFormMixin
from apps.properties.core.selectors import get_accessible_properties


class DashboardFilterForm(StyledFormMixin, forms.Form):
    property = forms.ModelChoiceField(required=False, queryset=None)
    start_date = forms.DateField(required=False, widget=forms.DateInput())
    end_date = forms.DateField(required=False, widget=forms.DateInput())

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['property'].queryset = get_accessible_properties(user)
        today = timezone.localdate()
        self.fields['start_date'].initial = today.replace(day=1)
        self.fields['end_date'].initial = today
