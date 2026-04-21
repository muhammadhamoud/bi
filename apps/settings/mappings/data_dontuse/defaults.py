# apps/settings/mappings/services/defaults.py

from django.db import transaction

from apps.settings.mappings.data_dontuse.day_of_week_defaults import seed_default_day_of_week_for_property
from apps.settings.mappings.data_dontuse.segment_defaults import seed_default_segments_for_property
from apps.settings.mappings.data_dontuse.room_type_defaults import seed_default_room_types_for_property


@transaction.atomic
def seed_default_mappings_for_property(property_obj, actor=None):
    seed_default_segments_for_property(property_obj, actor=actor)
    seed_default_day_of_week_for_property(property_obj, actor=actor)
    seed_default_room_types_for_property(property_obj, actor=actor)