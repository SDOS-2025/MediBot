from django import template
from django.urls import reverse

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get a value from a dictionary by key
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key, 0)

@register.simple_tag
def load_manager_url():
    """Return the URL to the load manager dashboard"""
    return reverse('load_dashboard')

@register.inclusion_tag('load_manager_button.html')
def load_manager_button():
    """Render a button that links to the load manager dashboard"""
    return {
        'url': reverse('load_dashboard')
    } 