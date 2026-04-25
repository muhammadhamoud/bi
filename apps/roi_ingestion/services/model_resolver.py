# from django.apps import apps
# from django.conf import settings


# def get_model_from_setting(setting_name: str, default_label: str):
#     label = getattr(settings, setting_name, default_label)
#     return apps.get_model(label, require_ready=True)


# def get_file_record_model():
#     return get_model_from_setting("ROI_FILE_RECORD_MODEL", "files.FileRecord")


# def get_property_model():
#     return get_model_from_setting("ROI_PROPERTY_MODEL", "propertycore.Property")


# def get_source_system_model():
#     return get_model_from_setting("ROI_SOURCE_SYSTEM_MODEL", "integrations.SourceSystem")


# def get_expected_file_definition_model():
#     return get_model_from_setting("ROI_EXPECTED_FILE_DEFINITION_MODEL", "files.ExpectedFileDefinition")


# apps/roi_ingestion/services/model_resolver.py

from __future__ import annotations

from importlib import import_module
from typing import Type

from django.apps import apps
from django.conf import settings
from django.db import models


def get_model_from_setting(setting_name: str, default_model_path: str) -> Type[models.Model]:
    """
    Resolve a Django model from settings.

    Supports:

    1. Django model label:
       "files.FileRecord"

    2. Full Python import path:
       "apps.dataops.files.models.FileRecord"
    """
    model_path = getattr(settings, setting_name, default_model_path)

    if not isinstance(model_path, str) or "." not in model_path:
        raise ValueError(
            f"{setting_name} must be a string like "
            f"'app_label.ModelName' or 'package.module.ModelName'."
        )

    parts = model_path.split(".")

    # Django app-label style: "files.FileRecord"
    if len(parts) == 2:
        app_label, model_name = parts
        return apps.get_model(app_label, model_name, require_ready=True)

    # Full Python path style: "apps.dataops.files.models.FileRecord"
    module_path = ".".join(parts[:-1])
    class_name = parts[-1]

    module = import_module(module_path)

    try:
        model_class = getattr(module, class_name)
    except AttributeError as exc:
        raise LookupError(
            f"Could not find model class '{class_name}' in module '{module_path}' "
            f"from setting {setting_name}={model_path!r}."
        ) from exc

    if not issubclass(model_class, models.Model):
        raise TypeError(
            f"{setting_name} resolved to {model_class!r}, but it is not a Django model."
        )

    return model_class


def get_file_record_model() -> Type[models.Model]:
    return get_model_from_setting(
        "ROI_FILE_RECORD_MODEL",
        "files.FileRecord",
    )


def get_property_model() -> Type[models.Model]:
    return get_model_from_setting(
        "ROI_PROPERTY_MODEL",
        "propertycore.Property",
    )


def get_source_system_model() -> Type[models.Model]:
    return get_model_from_setting(
        "ROI_SOURCE_SYSTEM_MODEL",
        "files.SourceSystem",
    )


def get_expected_file_definition_model() -> Type[models.Model]:
    return get_model_from_setting(
        "ROI_EXPECTED_FILE_DEFINITION_MODEL",
        "files.ExpectedFileDefinition",
    )