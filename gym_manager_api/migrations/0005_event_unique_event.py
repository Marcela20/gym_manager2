# Generated by Django 4.2.6 on 2023-10-15 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym_manager_api', '0004_remove_event_group_event_group'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='event',
            constraint=models.UniqueConstraint(fields=('date', 'hour', 'group'), name='unique_event'),
        ),
    ]