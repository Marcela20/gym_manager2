# Generated by Django 4.2.6 on 2023-10-21 13:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym_manager_api', '0007_remove_event_unique_event_remove_event_hour_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='duration',
            field=models.DurationField(default=datetime.timedelta(seconds=3600)),
        ),
        migrations.AddField(
            model_name='scheduler',
            name='duration',
            field=models.DurationField(default=datetime.timedelta(seconds=3600)),
        ),
    ]