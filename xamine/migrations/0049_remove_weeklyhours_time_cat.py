# Generated by Django 3.1.2 on 2020-11-05 03:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('xamine', '0048_timecategory_wed_hours'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='weeklyhours',
            name='time_cat',
        ),
    ]
