from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import CreateView

from apps.properties.core.services import set_current_property
from apps.core.common.access import SuperuserRequiredMixin
from apps.properties.core.models import Property
from apps.properties.core.forms import PropertyForm
from apps.settings.mappings.services.defaults import seed_default_mappings_for_property


# class SwitchPropertyView(LoginRequiredMixin, View):
#     def post(self, request, *args, **kwargs):
#         property_id = request.POST.get('property_id')
#         property_obj = set_current_property(request, property_id)
#         if property_obj:
#             messages.success(request, f'Active property switched to {property_obj.name}.')
#         else:
#             messages.error(request, 'Unable to switch property.')
#         return redirect(request.POST.get('next') or request.META.get('HTTP_REFERER') or 'dashboard:home')

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


class SwitchPropertyView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        property_id = request.POST.get('property_id')
        property_obj = set_current_property(request, property_id)

        if property_obj:
            messages.success(request, f'Active property switched to {property_obj.name}.')
        else:
            messages.error(request, 'Unable to switch property.')

        next_url = (
            request.POST.get('next')
            or request.META.get('HTTP_REFERER')
            or '/'
        )

        if property_id:
            parts = urlsplit(next_url)
            query = dict(parse_qsl(parts.query, keep_blank_values=True))
            query['property'] = str(property_id)
            next_url = urlunsplit((
                parts.scheme,
                parts.netloc,
                parts.path,
                urlencode(query),
                parts.fragment,
            ))

        return redirect(next_url)


from django.utils.deprecation import MiddlewareMixin

from apps.properties.core.models import Property
from apps.properties.core.selectors import get_accessible_properties

SESSION_KEY = "current_property_id"

class ActivePropertyMiddleware(MiddlewareMixin):
    SESSION_KEY = "current_property_id"

    def process_request(self, request):
        if not request.user.is_authenticated:
            return

        property_id = request.GET.get("property")
        if not property_id:
            return

        accessible_properties = get_accessible_properties(request.user)
        property_obj = accessible_properties.filter(id=property_id).first()

        if property_obj:
            request.session[self.SESSION_KEY] = property_obj.id
            request.current_property = property_obj


def get_current_property(request):
    if not request.user.is_authenticated:
        return None

    if hasattr(request, "current_property"):
        return request.current_property

    property_id = request.session.get(SESSION_KEY)
    if not property_id:
        return None

    property_obj = get_accessible_properties(request.user).filter(id=property_id).first()
    request.current_property = property_obj
    return property_obj


def set_current_property(request, property_id):
    if not request.user.is_authenticated or not property_id:
        return None

    property_obj = get_accessible_properties(request.user).filter(id=property_id).first()
    if not property_obj:
        return None

    request.session[SESSION_KEY] = property_obj.id
    request.current_property = property_obj
    return property_obj


from django.db import IntegrityError, transaction


class PropertyCreateView(SuperuserRequiredMixin, CreateView):
    model = Property
    form_class = PropertyForm
    success_url = reverse_lazy("dashboard:home")
    template_name = "properties/property_form.html"

    @transaction.atomic
    def form_valid(self, form):
        try:
            response = super().form_valid(form)

            property_obj = self.object
            actor = self.request.user

            transaction.on_commit(
                lambda: seed_default_mappings_for_property(
                    property_obj=property_obj,
                    actor=actor,
                    # domains=[
                    #     "segment",
                    #     "day_of_week",
                    #     "room_type",
                    #     "booking_source",
                    #     "origin",
                    # ],
                )
            )

            return response

        except IntegrityError:
            form.add_error(
                "name",
                "A property with the same generated name already exists.",
            )
            return self.form_invalid(form)
    

