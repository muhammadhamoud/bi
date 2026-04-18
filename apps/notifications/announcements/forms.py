from django import forms

from apps.core.common.forms import StyledFormMixin
from apps.properties.core.selectors import get_accessible_properties
from apps.usermanagement.roles.services import ROLE_ADMIN, ROLE_MANAGER, ROLE_MERCHANT_OWNER, ROLE_OPERATOR, ROLE_VIEWER
from apps.notifications.announcements.models import Announcement


class AnnouncementForm(StyledFormMixin, forms.ModelForm):
    target_roles = forms.MultipleChoiceField(
        required=False,
        choices=[(role, role) for role in [ROLE_ADMIN, ROLE_MANAGER, ROLE_OPERATOR, ROLE_MERCHANT_OWNER, ROLE_VIEWER]],
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Announcement
        fields = ['title', 'body', 'level', 'is_published', 'starts_at', 'ends_at', 'properties', 'target_roles', 'is_active']

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['properties'].queryset = get_accessible_properties(actor)
        if self.instance.pk:
            self.fields['target_roles'].initial = self.instance.target_role_list

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.target_roles = ','.join(self.cleaned_data.get('target_roles', []))
        if commit:
            instance.save()
            self.save_m2m()
        return instance
