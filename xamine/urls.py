from django.urls import path, include
from django.conf import settings

from xamine import views, apiviews


urlpatterns = [
    path('', views.index, name='index'),  # view dashboard

    path('order/', views.public_order, name='public_order'),  # Patient viewing of orders
    path('order/<int:order_id>/', views.order, name='order'),  # Internal viewing and submitting of orders
    path('order/<int:order_id>/upload', views.upload_file, name='submit_image'),  # Uploading images for order
    path('order/<int:order_id>/send', apiviews.patient_email, name='patient_view'),  # Send patient view email
    path('order/<int:order_id>/schedule', views.schedule_order, name='schedule_time'),  # Schedule our order
    path('order/<int:order_id>/save', views.save_order, name='save_order'),  # Save radiology report without finalizing.
    path('order/<int:order_id>/pdf_view', views.view_pdf, name="pdf_view"),
    path('order/<int:order_id>/pdf_download', views.download_pdf, name="pdf_download"),

    path('patient/<int:pat_id>/', views.patient, name='patient'),  # View patient info
    path('patient/', views.patient_lookup, name='patient_lookup'),  # lookup patients by DOB
    path('patient/new', views.new_patient, name='new_patient'),  # Submit new patient info
    path('patient/<int:pat_id>/new-order', views.new_order, name='new_order'),  # Start new order for patient

    path('image/<int:img_id>/remove', views.remove_file, name='remove_image'),  # Remove specified image

    path('patient-login/', views.loginPatient, name='patient_login'),  # lookup patients by DOB
    path('survey/<int:order_id>/', views.order_survey, name='order_survey'),  # Create survey for visit
    path('survey/<int:order_id>/save', views.submit_survey, name='submit_survey'),  # Submit survey of visit

    path('timesheet/', views.timesheet, name='timesheet'),  # Timesheet for logging employee hours
    path('reports/', views.reports, name='reports'),  # Dashboard page for previewing Productivity Reports
    path('reports/<int:user_id>/download/<str:week_of>/', views.download_excel, name='download_report'),  # Download Productivity Report of user
]

# Ensure the images and thumbnails can be loaded during development
if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)