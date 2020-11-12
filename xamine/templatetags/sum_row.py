from django import template

register = template.Library()

@register.filter
def sum_row(value):
    try:
        return value['mon_hours']+value['tues_hours']+value['wed_hours']+value['thur_hours'] + \
                value['fri_hours']+value['sat_hours']+value['sun_hours']
    except:
        return '0.00'