# Generated by Django 4.2.6 on 2023-10-21 11:03

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gym_manager_api', '0005_event_unique_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduler',
            name='first',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='scheduler',
            name='last',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
