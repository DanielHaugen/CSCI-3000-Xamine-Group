from django import template
from datetime import datetime

register = template.Library()

@register.filter
def date_str(value):
    return value.strftime('%Y-%m-%d')