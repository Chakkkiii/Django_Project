# yourapp/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='custom_range')
def custom_range(value):
    return range(value)


@register.filter(name='get_video_by_number')
def get_video_by_number(course, video_number):
    return course.get_video_by_number(video_number)

@register.filter
def get_option(obj, option):
    return getattr(obj, f'option{option}', '')