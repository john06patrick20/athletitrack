# core/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Allows dictionary lookup with a variable key in a template.
    Usage: {{ my_dictionary|get_item:my_variable }}
    """
    return dictionary.get(key)


# --- ADD THIS NEW FILTER TO YOUR EXISTING FILE ---
@register.filter
def add_attr(field, attr_string):
    key, value = attr_string.split(':', 1)
    return field.as_widget(attrs={key: value})

# --- THIS IS THE NEW FILTER YOU NEED TO ADD ---
@register.filter
def replace(value, arg):
    """
    Replaces all occurrences of arg's first part with the second part.
    'arg' should be a string in the format "find,replace".
    Usage: {{ my_string|replace:"find_this,replace_with_this" }}
    """
    if len(arg.split(',')) != 2:
        return value
    
    find_str, replace_str = arg.split(',')
    return value.replace(find_str, replace_str)
# --- END OF NEW FILTER --

@register.filter
def stat_group_slug(value):
    """
    Takes a stat name like "3 Pointers Made" and turns it into a slug
    like "3-pointers" for use in data attributes.
    """
    return value.lower().replace(' made', '').replace(' attempted', '').replace(' ', '-')
