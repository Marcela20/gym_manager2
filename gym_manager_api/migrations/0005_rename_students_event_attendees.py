# Generated by Django 4.2.4 on 2023-08-11 19:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gym_manager_api", "0004_rename_studens_group_students"),
    ]

    operations = [
        migrations.RenameField(
            model_name="event",
            old_name="students",
            new_name="attendees",
        ),
    ]
