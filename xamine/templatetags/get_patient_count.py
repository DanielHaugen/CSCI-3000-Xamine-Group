from django import template
import datetime

from xamine.models import TimeCategory, WeeklyHours, Order, Team, User
from xamine.utils import is_in_group

register = template.Library()

@register.simple_tag
def get_patient_count(staff, week_of=datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())):
    # try:
    end_week = week_of + datetime.timedelta(days=7)
    week_orders = Order.objects.filter(added_on__range=[week_of, end_week])

    if is_in_group(staff, "Administrators"):
        return "N/A"
    elif is_in_group(staff, "Receptionists"):
        return len(week_orders.filter(receptionist=staff))
    elif is_in_group(staff, ['Technicians', 'Radiologists']):
        if is_in_group(staff, 'Radiologists'):
            team = Team.objects.filter(radiologists__in=User.objects.filter(id=staff.id))
        else:
            team = Team.objects.filter(technicians__in=User.objects.filter(id=staff.id))
        return len(week_orders.filter(team__in=team))
    elif is_in_group(staff, "Physicians"):
        return len(week_orders.filter(patient__doctor=staff))

    return 'Error'
    # except:
    #     return 0