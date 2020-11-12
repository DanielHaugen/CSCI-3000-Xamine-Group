from django import template
from xamine.models import TimeCategory, WeeklyHours
import datetime

register = template.Library()

@register.simple_tag
def timed_in(staff, week_of=datetime.date.today() + datetime.timedelta(days=-datetime.date.today().weekday())):
    try:
        cat_list = WeeklyHours.objects.filter(employee=staff, week_of=week_of)[0]
        
        return cat_list
    except:
        return