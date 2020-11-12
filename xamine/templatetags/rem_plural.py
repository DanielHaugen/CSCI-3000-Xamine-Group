from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()

@register.filter
@stringfilter
def rem_plural(value):
    return re.sub("s$","", value)
