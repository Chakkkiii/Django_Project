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


@register.filter(name='getattr')
def get_attribute(value, arg):
    return getattr(value, arg, None)

@register.filter(name='get_val')
def get_val(dictionary, key):
    return dictionary.get(key)

@register.filter(name='get_by_id')
def get_by_id(queryset, value):
    try:
        return queryset.get(id=value)
    except queryset.model.DoesNotExist:
        return None
    

@register.filter(name='split_string')
def split_string(value, delimiter=","):
    return value.split(delimiter)

def get_week_videos(week_content, week):
    return week_content[week].videos


@register.filter
def get_key(dictionary, key):
    return dictionary.get(key, None)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, None)

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)