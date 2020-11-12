from django import template
import datetime

from xamine.models import Order, Team, User, Survey
from xamine.utils import is_in_group

register = template.Library()

@register.simple_tag
def get_feedback(staff, week_of=datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())):
    # try:
    end_week = week_of + datetime.timedelta(days=7)
    week_orders = Order.objects.filter(added_on__range=[week_of, end_week])

    avg = 0
    sum = 0
    rev_count = 0
    if is_in_group(staff, "Administrators"):
        return "N/A"
    elif is_in_group(staff, ['Technicians', 'Radiologists']):
        if is_in_group(staff, 'Radiologists'):
            team = Team.objects.filter(radiologists__in=User.objects.filter(id=staff.id))
        else:
            team = Team.objects.filter(technicians__in=User.objects.filter(id=staff.id))
        
        survey_list = Survey.objects.filter(order__in=week_orders.filter(team__in=team))
        rev_count = len(survey_list)
        for survey in survey_list:
            sum += survey.team_rating
    
    if rev_count > 0:
        avg = sum / rev_count
    

    return f'{avg:.1f} / 10 [{rev_count} Reviews]'
    # except:
    #     return 0