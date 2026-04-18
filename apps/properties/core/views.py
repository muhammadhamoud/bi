from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import CreateView

from apps.properties.core.services import set_current_property
from apps.core.common.access import SuperuserRequiredMixin
from apps.properties.core.models import Property
from apps.settings.mappings.data.defaults import seed_default_mappings_for_property
from apps.properties.core.forms import PropertyForm


class SwitchPropertyView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        property_id = request.POST.get('property_id')
        property_obj = set_current_property(request, property_id)
        if property_obj:
            messages.success(request, f'Active property switched to {property_obj.name}.')
        else:
            messages.error(request, 'Unable to switch property.')
        return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER') or 'dashboard:home')


from django.db import IntegrityError


class PropertyCreateView(SuperuserRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    success_url = reverse_lazy('dashboard:home')
    template_name = 'properties/property_form.html'

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            seed_default_mappings_for_property(
                property_obj=self.object,
                actor=self.request.user,
            )
            return response
        except IntegrityError:
            form.add_error('name', 'A property with the same generated name already exists.')
            return self.form_invalid(form)
    

