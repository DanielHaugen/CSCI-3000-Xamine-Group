# Generated by Django 3.1.1 on 2020-10-31 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xamine', '0044_auto_20201031_1914'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='survey',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]