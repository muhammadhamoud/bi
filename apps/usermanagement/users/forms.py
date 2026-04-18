from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm

from apps.core.common.forms import StyledFormMixin
from apps.usermanagement.users.selectors import get_assignable_properties, get_assignable_roles
from apps.usermanagement.users.services import sync_user_properties, sync_user_role

User = get_user_model()


class TailwindAuthenticationForm(StyledFormMixin, AuthenticationForm):
    remember_me = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email or username'


class TailwindPasswordResetForm(StyledFormMixin, PasswordResetForm):
    pass


class TailwindSetPasswordForm(StyledFormMixin, SetPasswordForm):
    pass


class TailwindPasswordChangeForm(StyledFormMixin, PasswordChangeForm):
    pass


class UserFilterForm(StyledFormMixin, forms.Form):
    q = forms.CharField(required=False, label='Search')
    role = forms.ChoiceField(required=False, choices=[])
    property = forms.ModelChoiceField(required=False, queryset=None)
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All statuses'), ('active', 'Active'), ('inactive', 'Inactive')],
    )

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [('', 'All roles')] + [(role, role) for role in get_assignable_roles(actor) + ['Admin', 'Manager', 'Operator', 'Merchant Owner', 'Viewer']]
        self.fields['property'].queryset = get_assignable_properties(actor)


class BaseUserManagementForm(StyledFormMixin, forms.ModelForm):
    role = forms.ChoiceField(required=False)
    properties = forms.ModelMultipleChoiceField(required=False, queryset=None)

    def __init__(self, *args, actor=None, **kwargs):
        self.actor = actor
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [('', 'Select role')] + [(role, role) for role in get_assignable_roles(actor)]
        self.fields['properties'].queryset = get_assignable_properties(actor)
        if self.instance.pk:
            self.fields['role'].initial = self.instance.primary_role
            self.fields['properties'].initial = self.instance.property_assignments.values_list('property_id', flat=True)

    def save(self, commit=True):
        instance = super().save(commit)
        if commit:
            sync_user_role(instance, self.cleaned_data.get('role'))
            sync_user_properties(instance, self.cleaned_data.get('properties', []), assigned_by=self.actor)
        return instance


class UserCreateForm(BaseUserManagementForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'display_name', 'job_title', 'phone_number', 'is_active']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.set_password(self.cleaned_data['password1'])
        if commit:
            instance.save()
            sync_user_role(instance, self.cleaned_data.get('role'))
            sync_user_properties(instance, self.cleaned_data.get('properties', []), assigned_by=self.actor)
        return instance


class UserUpdateForm(BaseUserManagementForm):
    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'display_name', 'job_title', 'phone_number', 'is_active']
