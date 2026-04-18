from apps.core.security.models import SecurityEvent


def log_security_event(*, category: str, event_type: str, user=None, property_obj=None, severity='info', object_repr='', details=None, ip_address=None):
    return SecurityEvent.objects.create(
        category=category,
        event_type=event_type,
        user=user,
        property=property_obj,
        severity=severity,
        object_repr=object_repr,
        details=details or {},
        ip_address=ip_address,
    )
