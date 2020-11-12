from django.contrib import admin

from django.core.mail import send_mail, BadHeaderError, EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.shortcuts import render, redirect

from xamine.models import Patient, Level, Order, Image, ModalityOption, Team, AppSetting, Survey, TimeCategory, WeeklyHours

admin.site.site_header = 'Xamine RIS Admin'


class ImageInline(admin.TabularInline):
    model = Image
    fields = ['label', 'image', 'added_on', 'user']
    readonly_fields = ['added_on', 'user']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ['added_on', 'last_edit']
    inlines = [ImageInline]


class TeamAdmin(admin.ModelAdmin):
    filter_horizontal = ['radiologists', 'technicians']

class PatientAdmin(admin.ModelAdmin):
    change_form_template = 'xamine/patient/change_form.html'
    
    def response_change(self, request, obj):
        if '_email-reminder' in request.POST:
            from_email = 'xamine-team3@daniel-haugen.com'
            recipient_list = ['dlhaug7343@ung.edu','dlhaugen1039@gmail.com']
            subject = 'Xamine Update'
            patient_dict = {'first_name':'Bob', 'visit_date':'October 19th, 2020'}
            html_message = render_to_string(
                template_name = 'mail_templates/email_message.html',
                context = patient_dict
            )
            self.message_user(request, "This villain is now unique")
            try:
                msg = EmailMessage(subject=subject, body=html_message, from_email=from_email, to=recipient_list)
                msg.content_subtype = "html"
                msg.send()
                #send_mail(subject, message, from_email, recipient_list)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('success')
            #return HttpResponseRedirect(".")
        return super().response_change(request, obj)



admin.site.register(Patient)
admin.site.register(Level)
admin.site.register(AppSetting)
# admin.site.register(Image)
admin.site.register(ModalityOption)
admin.site.register(Team, TeamAdmin)
admin.site.register(Survey)
admin.site.register(TimeCategory)
admin.site.register(WeeklyHours)