from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import FormView

from apps.properties.core.models import Property
from apps.settings.mappings.forms.copy import MappingCopyForm
from apps.settings.mappings.services import MAPPING_DOMAIN_REGISTRY
from apps.settings.mappings.services.copy_service import MappingCopyService


class MappingCopyView(LoginRequiredMixin, FormView):
    template_name = "settings/mappings/copy_form.html"
    form_class = MappingCopyForm

    def dispatch(self, request, *args, **kwargs):
        self.domain_key = kwargs["domain_key"]
        self.target_property = get_object_or_404(Property, pk=kwargs["property_id"])
        self.domain_config = MAPPING_DOMAIN_REGISTRY[self.domain_key]
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["target_property"] = self.target_property

        # replace with your property access filter
        kwargs["property_queryset"] = Property.objects.filter(is_active=True).order_by("name")
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["target_property"] = self.target_property
        context["domain_key"] = self.domain_key
        context["page_title"] = f"Copy {self.domain_config.get('label', self.domain_key.title())}"
        return context

    def form_valid(self, form):
        service = MappingCopyService(
            domain_key=self.domain_key,
            source_property=form.cleaned_data["source_property"],
            target_property=self.target_property,
            copy_groups=form.cleaned_data["copy_groups"],
            copy_categories=form.cleaned_data["copy_categories"],
            copy_mappings=form.cleaned_data["copy_mappings"],
            copy_details=form.cleaned_data["copy_details"],
            mode=form.cleaned_data["mode"],
        )

        stats = service.execute()

        messages.success(
            self.request,
            (
                f"Copy completed. "
                f"Groups: +{stats.groups_created} / ~{stats.groups_updated} / ={stats.groups_skipped}, "
                f"Categories: +{stats.categories_created} / ~{stats.categories_updated} / ={stats.categories_skipped}, "
                f"Mappings: +{stats.mappings_created} / ~{stats.mappings_updated} / ={stats.mappings_skipped}, "
                f"Details: +{stats.details_created} / ~{stats.details_updated} / ={stats.details_skipped}"
            ),
        )
        return redirect(self.request.path)