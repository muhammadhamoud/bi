from apps.core.common.access import get_accessible_properties


def set_current_property(request, property_id):
    property_obj = get_accessible_properties(request.user).filter(id=property_id).first()
    if property_obj:
        request.session['current_property_id'] = property_obj.id
    return property_obj
