from django.conf import settings
from django.shortcuts import render
from django.core.mail import send_mail, EmailMessage, BadHeaderError
from django.urls import reverse
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

from xamine.models import OrderKey, AppSetting, Order
import random
import string

from xamine.tasks import send_email


@api_view(['GET'])
def patient_email(request, order_id):
    """ Handles sending email to patient to view order """

    # Establish where the app is hosted
    host = "abisalimi.pythonanywhere.com/"

    # attempt to send email
    try:
        # Attempt to grab order via order_id from url. 404 if not found.
        try:
            cur_order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            return_data = {
                'status': 'fail',
                'message': f'Email not sent! Order does not exist',
            }
            return Response(return_data, status=status.HTTP_400_BAD_REQUEST)

        # Establish our URL and recipient, the patient's email
        url = f"{request.build_absolute_uri('/')}patient-login/"
        to_email = cur_order.patient.email_info

        # Set up our message content
        html_content = "Imaging report has been emailed to you: <br><br>" + url

        if AppSetting.get_setting('EMAIL_TOGGLE') == 'True':
            # Send patient our email
            from_email = '[REDACTED]'
            subject = 'Xamine RIS - Records Update'
            patient_dict = {
                'first_name': cur_order.patient.first_name,
                'url': url
            }
            cc_list = ['[REDACTED]']
            html_message = render_to_string(
                template_name = 'mail_templates/email_message.html',
                context = patient_dict
            )
            try:
                msg = EmailMessage(subject=subject, body=html_message, from_email=from_email, to=[to_email], cc=cc_list)
                msg.content_subtype = "html"
                msg.send()
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            #send_email([to_email], '[REDACTED]', 'RIS Report is Ready', html_content)
            message = 'Email Sent!'
        else:
            message = 'Link created!'

        # Return JSON to confirm success
        return_data = {
            'status': 'ok',
            'message': message,
            'link': url,
        }
        return Response(return_data, status=status.HTTP_201_CREATED)
    except Exception as e:
        # Return JSON to express failure
        return_data = {
            'status': 'fail',
            'message': f'Email not sent!{to_email}',
        }
        return Response(return_data, status=status.HTTP_400_BAD_REQUEST)


def random_string(string_length=128):
    """ Gets random string of desired length """
    # Get list of all lowercase and uppercase letters and return the desired number of them randomly
    letters = string.ascii_lowercase + string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(string_length))
