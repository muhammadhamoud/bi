from django import template

from apps.analytics.kpi.services import kpi_calculations

register = template.Library()


@register.simple_tag
def occupancy(rooms_sold, available_rooms):
    return kpi_calculations.occupancy(rooms_sold, available_rooms)


@register.simple_tag
def adr(room_revenue, rooms_sold):
    return kpi_calculations.adr(room_revenue, rooms_sold)


@register.simple_tag
def revpar(room_revenue, available_rooms):
    return kpi_calculations.revpar(room_revenue, available_rooms)


@register.simple_tag
def percentage_change(current_value, previous_value):
    return kpi_calculations.percentage_change(current_value, previous_value)


@register.simple_tag
def absolute_change(current_value, previous_value):
    return kpi_calculations.absolute_change(current_value, previous_value)


@register.simple_tag
def achieved_goal_percentage(actual_value, goal_value):
    return kpi_calculations.achieved_goal_percentage(actual_value, goal_value)
