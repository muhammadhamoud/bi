from django import forms

from apps.core.common.forms import StyledFormMixin
from apps.usermanagement.profiles.models import Profile
from apps.usermanagement.users.models import User


class SelfProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'display_name', 'job_title', 'phone_number']


class ProfilePreferencesForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'timezone', 'theme_preference', 'locale', 'bio', 'receive_email_notifications', 'receive_product_announcements']
