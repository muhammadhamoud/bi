from django import forms

from apps.properties.core.models import Property


class MappingCopyForm(forms.Form):
    COPY_MODE_CHOICES = (
        ("skip", "Skip existing"),
        ("update", "Update existing"),
    )

    source_property = forms.ModelChoiceField(
        queryset=Property.objects.filter(is_active=True).order_by("name"),
        required=True,
    )
    copy_groups = forms.BooleanField(required=False, initial=True)
    copy_categories = forms.BooleanField(required=False, initial=True)
    copy_mappings = forms.BooleanField(required=False, initial=True)
    copy_details = forms.BooleanField(required=False, initial=False)
    mode = forms.ChoiceField(choices=COPY_MODE_CHOICES, initial="skip")

    def __init__(self, *args, target_property=None, property_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_property = target_property

        if property_queryset is not None:
            self.fields["source_property"].queryset = property_queryset

        if target_property:
            self.fields["source_property"].queryset = (
                self.fields["source_property"].queryset.exclude(pk=target_property.pk)
            )

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get("copy_mappings"):
            self.add_error("copy_mappings", "Mappings must be enabled for this copy action.")

        return cleaned_data