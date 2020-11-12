from xamine.models import Order, WeeklyHours, User, Survey, Team
from xamine.utils import is_in_group
from django.http import Http404, HttpResponse
from datetime import datetime as dt
from io import BytesIO
import pandas as pd
import datetime

def generate_excel(user_id, week_of):
    try:
        cur_user = User.objects.get(id=user_id)
    except Order.DoesNotExist:
        raise Http404

    # Generate Excel file
    output = BytesIO()

    cur_week = datetime.datetime.strptime(week_of, "%Y-%m-%d")
    tmp_dict = gen_dictionary(cur_user, cur_week)
    df = pd.DataFrame(tmp_dict)

    cur_offset = 7
    writer = pd.ExcelWriter(output, engine='xlsxwriter', options={'strings_to_numbers': True})
    df.to_excel(writer, sheet_name='Sheet1', startcol = 0, startrow = cur_offset+2, header=False)

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    # Default Text Size
    workbook.formats[0].set_font_size(12)
    workbook.formats[0].set_font_name('Times New Roman')
    # Draw Custom Table Header
    header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'border':1, 'font_size':14, 
                                        'font_name':'Times New Roman', 'align': 'center'})
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(cur_offset+1, col_num+1, value, header_format)

    # Title Format
    cell_format = workbook.add_format({'font_size':18, 'font_name':'Times New Roman', 'bold':True})
    # Day Labels Format
    label_format = workbook.add_format({'font_size':14, 'font_name':'Times New Roman', 'bold':True, 'align':'center'})
    # Table Format
    table_format = workbook.add_format({'font_size':12, 'font_name':'Times New Roman'})
    # Centered Format
    centered_format = workbook.add_format({'font_size':12, 'font_name':'Times New Roman', 'align': 'center'})
    
    # Worksheet Title
    cur_week = dt.strptime(week_of, "%Y-%m-%d").strftime("%B %-d, %Y")
    tmp_str = f'Productivity Report for {cur_user.first_name} {cur_user.last_name}, for the week of {cur_week}'
    worksheet.write_string(1, 1, tmp_str, cell_format)

    # User Details Section
    worksheet.write_string(3, 1, 'Username:', label_format)
    worksheet.merge_range(3,2, 3,3, cur_user.username, centered_format)

    worksheet.write_string(3, 4, 'Email:', label_format)
    worksheet.merge_range(3,5, 3,6, cur_user.email, centered_format)

    worksheet.write_string(3, 7, 'Pat. Count:', label_format)
    worksheet.write_string(3, 8, str(get_patient_count(cur_user, dt.strptime(week_of, "%Y-%m-%d"))), centered_format)

    worksheet.write_string(5, 1, 'Last Login:', label_format)
    worksheet.merge_range(5,2, 5,3, str(cur_user.last_login.strftime("%B %-d, %Y")), centered_format)

    worksheet.write_string(5, 4, 'Joined on:', label_format)
    worksheet.merge_range(5,5, 5,6, str(cur_user.date_joined.strftime("%B %-d, %Y")), centered_format)

    worksheet.write_string(5, 7, 'Pat. Rating:', label_format)
    worksheet.merge_range(5,8, 5,9, get_feedback(cur_user, dt.strptime(week_of, "%Y-%m-%d")))

    # Set the columns widths.
    worksheet.set_column('B:I', 12)
    
    worksheet.write_string(cur_offset, 2, 'Monday', label_format)
    worksheet.write_string(cur_offset, 3, 'Tuesday', label_format)
    worksheet.write_string(cur_offset, 4, 'Wednesday', label_format)
    worksheet.write_string(cur_offset, 5, 'Thursday', label_format)
    worksheet.write_string(cur_offset, 6, 'Friday', label_format)
    worksheet.write_string(cur_offset, 7, 'Saturday', label_format)
    worksheet.write_string(cur_offset, 8, 'Sunday', label_format)

    if tmp_dict['Category'] == []:
        worksheet.merge_range(cur_offset+2,1, cur_offset+2,8, 'No timesheet recorded for this user for this week.', centered_format)
        worksheet.write(cur_offset+2, 0, '0', header_format)
    else:
        chart = workbook.add_chart({'type': 'line'})
        for i in range(len(df['Category'])):
            chart.add_series({
                'name': ['Sheet1', cur_offset+2+i,1],
                'categories': ['Sheet1', cur_offset+1,2, cur_offset+1,8],
                'values': ['Sheet1', cur_offset+2+i,2, cur_offset+2+i,8],
                'marker': {'type': 'circle'}
                })
        chart.set_title({'name': f'Hours Logged - Week of {cur_week}'})
        chart.set_size({'width': 600, 'height': 450})
        worksheet.insert_chart(f'K{cur_offset}', chart)
    
    # Previous Week
    prev_week = dt.strptime(week_of, "%Y-%m-%d") - datetime.timedelta(weeks=1)
    prev_tmp_dict = gen_dictionary(cur_user, prev_week)
    df_prev = pd.DataFrame(prev_tmp_dict)
    
    vert_offset = cur_offset + len(df['Category']) + 6
    tmp_str = f'Previous Week Records - Week of {prev_week.strftime("%B %-d, %Y")}'
    worksheet.write_string(vert_offset-2, 2, tmp_str, cell_format)

    # If no timesheet is found for this week
    if prev_tmp_dict['Category'] == []:
        worksheet.merge_range(vert_offset+2,1, vert_offset+2,8, 'No timesheet recorded for this user for this week.', centered_format)
        worksheet.write(vert_offset+2, 0, '0', header_format)

    for col_num, value in enumerate(df_prev.columns.values):
        worksheet.write(vert_offset+1, col_num+1, value, header_format)
    df_prev.to_excel(writer, sheet_name='Sheet1', startcol = 0, startrow = vert_offset+2, header=False)

    worksheet.write_string(vert_offset, 2, 'Monday', label_format)
    worksheet.write_string(vert_offset, 3, 'Tuesday', label_format)
    worksheet.write_string(vert_offset, 4, 'Wednesday', label_format)
    worksheet.write_string(vert_offset, 5, 'Thursday', label_format)
    worksheet.write_string(vert_offset, 6, 'Friday', label_format)
    worksheet.write_string(vert_offset, 7, 'Saturday', label_format)
    worksheet.write_string(vert_offset, 8, 'Sunday', label_format)

    writer.save()
    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={cur_user}_{week_of}.xlsx'
    
    return response

def gen_dictionary(user, week_of):
    dates = []
    for i in range(0, 7):
        day = week_of + datetime.timedelta(days=i)
        dates.append(day.strftime("%Y-%m-%d"))

    dictionary = {'Category': [], dates[0]: [], dates[1]: [], 
                dates[2]: [], dates[3]: [], dates[4]: [], 
                dates[5]: [], dates[6]: []}

    try:
        query = list(WeeklyHours.objects.get(employee=user, week_of=week_of).week.all().values('name',
            'mon_hours','tues_hours','wed_hours','thur_hours','fri_hours','sat_hours','sun_hours'))
        
        for cat in query:
            dictionary['Category'].append(cat['name'])
            dictionary[dates[0]].append(cat['mon_hours'])
            dictionary[dates[1]].append(cat['tues_hours'])
            dictionary[dates[2]].append(cat['wed_hours'])
            dictionary[dates[3]].append(cat['thur_hours'])
            dictionary[dates[4]].append(cat['fri_hours'])
            dictionary[dates[5]].append(cat['sat_hours'])
            dictionary[dates[6]].append(cat['sun_hours'])

    except WeeklyHours.DoesNotExist:
        # Timesheet not provided for this user on this week
        pass

    return dictionary

def get_patient_count(staff, week_of=datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())):
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

def get_feedback(staff, week_of=datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())):
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


