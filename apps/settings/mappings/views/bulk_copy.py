from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView

from apps.core.common.mixins import BreadcrumbMixin
from apps.properties.core.selectors import get_accessible_properties
from apps.settings.mappings.forms.bulk_copy import BulkMappingCopyForm
from apps.settings.mappings.services.bulk_copy_service import BulkMappingCopyService
from apps.settings.mappings.views.common import MappingManageMixin


class BulkMappingCopyView(MappingManageMixin, BreadcrumbMixin, FormView):
    template_name = "settings/mappings/bulk_copy_form.html"
    form_class = BulkMappingCopyForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["actor"] = self.request.user
        kwargs["property_queryset"] = get_accessible_properties(self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Copy Settings Between Properties"
        context["breadcrumbs"] = [
            ("Dashboard", reverse("dashboard:home")),
            ("Settings", ""),
            ("Mappings", reverse("settings_mappings:overview")),
            ("Bulk Copy", ""),
        ]
        return context

    def form_valid(self, form):
        result = BulkMappingCopyService(
            source_property=form.cleaned_data["source_property"],
            target_property=form.cleaned_data["target_property"],
            domain_keys=form.cleaned_data["domain_keys"],
            copy_groups=form.cleaned_data["copy_groups"],
            copy_categories=form.cleaned_data["copy_categories"],
            copy_mappings=form.cleaned_data["copy_mappings"],
            copy_details=form.cleaned_data["copy_details"],
            mode=form.cleaned_data["mode"],
        ).execute()

        messages.success(
            self.request,
            f"Copy completed for {len(result.results)} settings model(s)."
        )
        return redirect("settings_mappings:overview")