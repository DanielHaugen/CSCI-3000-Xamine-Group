# Generated by Django 3.1.2 on 2020-11-11 02:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xamine', '0050_auto_20201104_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='weeklyhours',
            name='patient_count',
            field=models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(255), django.core.validators.MinValueValidator(0)]),
            preserve_default=False,
        ),
    ]