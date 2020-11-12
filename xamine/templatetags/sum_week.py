from django import template
from xamine.models import TimeCategory, WeeklyHours
import datetime

register = template.Library()

@register.simple_tag
def sum_week(staff, week_of=datetime.date.today() + datetime.timedelta(days=-datetime.date.today().weekday())):
    try:
        cat_list = WeeklyHours.objects.filter(employee=staff, week_of=week_of)[0].week.all()
        sum = 0
        for cats in cat_list:
            sum += cats.mon_hours + cats.tues_hours + cats.wed_hours + cats.thur_hours + cats.fri_hours + \
                cats.sat_hours + cats.sun_hours
        
        return sum
    except:
        return '0.00'