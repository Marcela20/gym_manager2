# Generated by Django 4.2.6 on 2023-12-08 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym_manager_api', '0011_scheduler_students_alter_scheduler_repeat_on'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='students',
        ),
        migrations.AddField(
            model_name='scheduler',
            name='start_hour',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
