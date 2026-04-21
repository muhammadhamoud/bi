from django import forms

from apps.core.common.forms import StyledFormMixin
from apps.properties.core.selectors import get_accessible_properties
from apps.settings.mappings.services import MAPPING_DOMAIN_REGISTRY


class BulkMappingCopyForm(StyledFormMixin, forms.Form):
    COPY_MODE_CHOICES = (
        ("skip", "Skip existing"),
        ("update", "Update existing"),
    )

    source_property = forms.ModelChoiceField(
        queryset=None,
        required=True,
        label="Copy from property",
    )
    target_property = forms.ModelChoiceField(
        queryset=None,
        required=True,
        label="Copy to property",
    )

    domain_keys = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Settings models to copy",
    )

    copy_groups = forms.BooleanField(required=False, initial=True, label="Groups")
    copy_categories = forms.BooleanField(required=False, initial=True, label="Categories")
    copy_mappings = forms.BooleanField(required=False, initial=True, label="Mappings")
    copy_details = forms.BooleanField(required=False, initial=False, label="Details")

    mode = forms.ChoiceField(
        choices=COPY_MODE_CHOICES,
        initial="skip",
        widget=forms.RadioSelect,
        label="Copy mode",
    )

    def __init__(self, *args, actor=None, property_queryset=None, **kwargs):
        self.actor = actor
        super().__init__(*args, **kwargs)

        properties = property_queryset or get_accessible_properties(actor)

        self.fields["source_property"].queryset = properties
        self.fields["target_property"].queryset = properties

        self.fields["domain_keys"].choices = [
            (key, config.get("label", key.replace("_", " ").title()))
            for key, config in MAPPING_DOMAIN_REGISTRY.items()
        ]

        self._apply_custom_ui()

    def _apply_custom_ui(self):
        select_classes = (
            "w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm "
            "text-slate-900 shadow-sm outline-none transition "
            "focus:border-blue-500 focus:ring-2 focus:ring-blue-200 "
            "dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 "
            "dark:focus:border-blue-400 dark:focus:ring-blue-500/20"
        )

        checkbox_classes = (
            "h-4 w-4 rounded border-slate-300 text-blue-600 "
            "focus:ring-2 focus:ring-blue-200 dark:border-slate-600 dark:bg-slate-800"
        )

        radio_classes = (
            "h-4 w-4 border-slate-300 text-blue-600 "
            "focus:ring-2 focus:ring-blue-200 dark:border-slate-600 dark:bg-slate-800"
        )

        self.fields["source_property"].widget.attrs.update({
            "class": select_classes,
        })
        self.fields["target_property"].widget.attrs.update({
            "class": select_classes,
        })

        for field_name in ("copy_groups", "copy_categories", "copy_mappings", "copy_details"):
            self.fields[field_name].widget.attrs.update({
                "class": checkbox_classes,
            })

        self.fields["domain_keys"].widget.attrs.update({
            "class": checkbox_classes,
        })

        self.fields["mode"].widget.attrs.update({
            "class": radio_classes,
        })

    def clean(self):
        cleaned_data = super().clean()

        source_property = cleaned_data.get("source_property")
        target_property = cleaned_data.get("target_property")

        if source_property and target_property and source_property.pk == target_property.pk:
            self.add_error("target_property", "Source and target property cannot be the same.")

        if not cleaned_data.get("domain_keys"):
            self.add_error("domain_keys", "Please select at least one settings model.")

        if not any([
            cleaned_data.get("copy_groups"),
            cleaned_data.get("copy_categories"),
            cleaned_data.get("copy_mappings"),
            cleaned_data.get("copy_details"),
        ]):
            raise forms.ValidationError("Select at least one structure item to copy.")

        if cleaned_data.get("copy_details") and not cleaned_data.get("copy_mappings"):
            self.add_error("copy_mappings", "Mappings must be selected when copying details.")

        return cleaned_data